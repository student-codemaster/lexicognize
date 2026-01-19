from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import tempfile
import uuid
from datetime import datetime

from app.utils.pdf_extractor import PDFExtractor
from app.utils.model_manager import ModelManager

router = APIRouter()

class PDFProcessRequest(BaseModel):
    pdf_file: UploadFile
    operations: List[str] = ["extract", "summarize", "simplify"]
    summary_model: Optional[str] = None
    simplification_model: Optional[str] = None
    max_length: int = 512
    min_length: int = 50

@router.post("/process")
async def process_pdf(
    file: UploadFile = File(...),
    operations: List[str] = ["extract", "summarize", "simplify"],
    summary_model: Optional[str] = None,
    simplification_model: Optional[str] = None,
    max_length: int = 512,
    min_length: int = 50
):
    """
    Process PDF: Extract text, summarize, and simplify
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create unique ID for this processing job
    process_id = str(uuid.uuid4())
    
    # Save uploaded PDF
    pdf_dir = "data/processed_pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    pdf_path = os.path.join(pdf_dir, f"{process_id}_{file.filename}")
    
    with open(pdf_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    results = {
        "process_id": process_id,
        "filename": file.filename,
        "operations": operations,
        "timestamp": datetime.now().isoformat()
    }
    
    # Extract text from PDF
    if "extract" in operations:
        try:
            extractor = PDFExtractor()
            extracted_text = extractor.extract_text(pdf_path)
            
            results["extraction"] = {
                "status": "success",
                "text_length": len(extracted_text),
                "text_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
            }
            
            # Save extracted text
            text_path = pdf_path.replace('.pdf', '_extracted.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            
        except Exception as e:
            results["extraction"] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Generate summary if requested
    if "summarize" in operations and results.get("extraction", {}).get("status") == "success":
        try:
            # Use default model if not specified
            if not summary_model:
                available_models = ModelManager.get_available_models()
                summary_models = [m for m in available_models if "summary" in m.lower() or "bart" in m.lower()]
                summary_model = summary_models[0] if summary_models else None
            
            if summary_model:
                summary = await ModelManager.generate_summary(
                    model_name=summary_model,
                    text=extracted_text,
                    max_length=max_length,
                    min_length=min_length
                )
                
                results["summary"] = {
                    "status": "success",
                    "model_used": summary_model,
                    "summary": summary,
                    "summary_length": len(summary)
                }
                
                # Save summary
                summary_path = pdf_path.replace('.pdf', '_summary.txt')
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
            else:
                results["summary"] = {
                    "status": "skipped",
                    "reason": "No summary model available"
                }
                
        except Exception as e:
            results["summary"] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Generate simplification if requested
    if "simplify" in operations:
        try:
            # Use text to simplify (either original or summary)
            text_to_simplify = extracted_text
            if "summary" in results and results["summary"]["status"] == "success":
                text_to_simplify = results["summary"]["summary"]
            
            # Use default model if not specified
            if not simplification_model:
                available_models = ModelManager.get_available_models()
                simplification_models = [m for m in available_models if "simplify" in m.lower() or "pegasus" in m.lower()]
                simplification_model = simplification_models[0] if simplification_models else None
            
            if simplification_model:
                simplified = await ModelManager.generate_simplification(
                    model_name=simplification_model,
                    text=text_to_simplify,
                    max_length=max_length,
                    min_length=min_length
                )
                
                results["simplification"] = {
                    "status": "success",
                    "model_used": simplification_model,
                    "simplified_text": simplified,
                    "simplified_length": len(simplified)
                }
                
                # Save simplified text
                simplified_path = pdf_path.replace('.pdf', '_simplified.txt')
                with open(simplified_path, 'w', encoding='utf-8') as f:
                    f.write(simplified)
            else:
                results["simplification"] = {
                    "status": "skipped",
                    "reason": "No simplification model available"
                }
                
        except Exception as e:
            results["simplification"] = {
                "status": "failed",
                "error": str(e)
            }
    
    return results

@router.get("/results/{process_id}")
async def get_processing_results(process_id: str):
    """Get results of PDF processing"""
    results_dir = "data/processed_pdfs"
    
    # Look for files with this process_id
    results_files = []
    for file in os.listdir(results_dir):
        if file.startswith(process_id):
            file_path = os.path.join(results_dir, file)
            file_type = "unknown"
            
            if file.endswith('.pdf'):
                file_type = "original_pdf"
            elif file.endswith('_extracted.txt'):
                file_type = "extracted_text"
            elif file.endswith('_summary.txt'):
                file_type = "summary"
            elif file.endswith('_simplified.txt'):
                file_type = "simplified_text"
            
            results_files.append({
                "filename": file,
                "type": file_type,
                "size": os.path.getsize(file_path),
                "path": file_path
            })
    
    return {
        "process_id": process_id,
        "files": results_files
    }

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download processed file"""
    file_path = os.path.join("data/processed_pdfs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@router.get("/history")
async def get_processing_history():
    """Get history of all PDF processing jobs"""
    history = []
    results_dir = "data/processed_pdfs"
    
    if os.path.exists(results_dir):
        # Group files by process_id
        files_by_process = {}
        
        for file in os.listdir(results_dir):
            if '_' in file:
                process_id = file.split('_')[0]
                if process_id not in files_by_process:
                    files_by_process[process_id] = []
                files_by_process[process_id].append(file)
        
        for process_id, files in files_by_process.items():
            # Get timestamp from first file
            first_file = files[0]
            file_path = os.path.join(results_dir, first_file)
            
            history.append({
                "process_id": process_id,
                "timestamp": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                "files": files,
                "file_count": len(files)
            })
    
    return {"history": sorted(history, key=lambda x: x["timestamp"], reverse=True)}