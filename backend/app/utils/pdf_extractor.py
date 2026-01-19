import pdfplumber
import PyPDF2
import pytesseract
from PIL import Image
import io
import os
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str, use_ocr: bool = False) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: Whether to use OCR for scanned PDFs
        
        Returns:
            Extracted text as string
        """
        text_parts = []
        
        try:
            # First try with pdfplumber (works well for text-based PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    elif use_ocr:
                        # If no text found and OCR is enabled, try OCR
                        ocr_text = self._extract_with_ocr(page)
                        text_parts.append(f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}")
            
            # If pdfplumber didn't extract text, try PyPDF2
            if not any(text_parts):
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            # If still no text and OCR is enabled, try full document OCR
            if not any(text_parts) and use_ocr:
                ocr_text = self._extract_with_ocr_full(pdf_path)
                text_parts.append(ocr_text)
            
            extracted_text = "\n\n".join(text_parts)
            
            # Clean up the text
            extracted_text = self._clean_text(extracted_text)
            
            logger.info(f"Extracted {len(extracted_text)} characters from {pdf_path}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def _extract_with_ocr(self, page) -> str:
        """Extract text from page image using OCR"""
        try:
            # Convert page to image
            image = page.to_image(resolution=300)
            # Convert to PIL Image
            pil_image = image.original
            
            # Use pytesseract for OCR
            text = pytesseract.image_to_string(pil_image, lang='eng')
            return text
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""
    
    def _extract_with_ocr_full(self, pdf_path: str) -> str:
        """Extract text from entire PDF using OCR"""
        # This is a simplified version - in production, you might want to use
        # a dedicated OCR service or library
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove page number markers if they're just numbers
        import re
        cleaned_text = re.sub(r'^\s*\d+\s*$', '', cleaned_text, flags=re.MULTILINE)
        
        return cleaned_text
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """Extract metadata from PDF"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get document info
                info = pdf_reader.metadata
                if info:
                    metadata = {
                        "title": info.get('/Title', ''),
                        "author": info.get('/Author', ''),
                        "creator": info.get('/Creator', ''),
                        "producer": info.get('/Producer', ''),
                        "creation_date": info.get('/CreationDate', ''),
                        "modification_date": info.get('/ModDate', '')
                    }
                
                # Get document properties
                metadata.update({
                    "page_count": len(pdf_reader.pages),
                    "is_encrypted": pdf_reader.is_encrypted,
                    "file_size": os.path.getsize(pdf_path)
                })
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
        
        return metadata
    
    def extract_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """Extract images from PDF"""
        image_paths = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    images = page.images
                    
                    for img_num, img in enumerate(images):
                        if output_dir:
                            os.makedirs(output_dir, exist_ok=True)
                            img_filename = f"page_{page_num + 1}_img_{img_num + 1}.png"
                            img_path = os.path.join(output_dir, img_filename)
                            
                            # Save the image
                            img_data = img["stream"].get_data()
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            
                            image_paths.append(img_path)
            
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
        
        return image_paths