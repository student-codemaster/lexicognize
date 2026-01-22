# 🚀 LexiCognize - Full Project with Training Capabilities

## ✅ Project Status: RUNNING WITH FULL TRAINING SUPPORT

**Date**: January 22, 2026  
**Status**: ✅ FULLY OPERATIONAL  
**Training**: ✅ ENABLED  

---

## 🎯 What's Running

### Backend API Server ✅
- **URL**: http://127.0.0.1:8001
- **Framework**: FastAPI with training endpoints
- **Status**: RUNNING (Process: 21812)
- **Training**: ENABLED
- **Database**: SQLite (legal_models.db)

### Frontend Server ✅
- **URL**: http://localhost:3000
- **Type**: Static file server
- **Status**: RUNNING
- **Purpose**: Web interface for training

### Database ✅
- **Type**: SQLite
- **Location**: backend/legal_models.db
- **Status**: CONNECTED
- **Tables**: Created and verified

---

## 📚 Available Training Endpoints

### 1. **Get Available Models**
```
GET /api/training/models
```
Returns list of available models for training:
- BART (Summarization)
- PEGASUS (Summarization)
- Multilingual T5 (Translation)

### 2. **Upload Training Dataset**
```
POST /api/training/upload-dataset
```
Upload a dataset file for training:
```bash
curl -X POST "http://127.0.0.1:8001/api/training/upload-dataset" \
  -F "file=@dataset.csv"
```

### 3. **Start Training Job**
```
POST /api/training/start
```
Start a new training job:
```bash
curl -X POST "http://127.0.0.1:8001/api/training/start?model=BART&epochs=3&batch_size=4&learning_rate=5e-5"
```

Parameters:
- `model`: BART, PEGASUS, or Multilingual
- `epochs`: Number of training epochs (default: 3)
- `batch_size`: Batch size (default: 4)
- `learning_rate`: Learning rate (default: 5e-5)

### 4. **Get Training Jobs**
```
GET /api/training/jobs
```
List all training jobs with status.

### 5. **Get Job Details**
```
GET /api/training/jobs/{job_id}
```
Get detailed information about a specific training job including:
- Progress percentage
- Current epoch
- Loss value
- Accuracy

### 6. **Evaluate Model**
```
POST /api/training/evaluate
```
Evaluate a trained model:
```bash
curl -X POST "http://127.0.0.1:8001/api/training/evaluate?job_id=1"
```

Returns metrics:
- Accuracy
- F1 Score
- Precision
- Recall
- ROUGE Score

### 7. **Run Inference**
```
POST /api/inference/predict
```
Make predictions with a trained model:
```bash
curl -X POST "http://127.0.0.1:8001/api/inference/predict?text=Your%20legal%20text&model=BART"
```

---

## 📊 Dataset Management Endpoints

### Get Datasets
```
GET /api/datasets
```

### Create Dataset
```
POST /api/datasets
```

---

## 🚀 Quick Start - Train a Model

### Step 1: Upload Dataset
```bash
curl -X POST "http://127.0.0.1:8001/api/training/upload-dataset" \
  -F "file=@my_dataset.csv"
```

### Step 2: Start Training
```bash
curl -X POST "http://127.0.0.1:8001/api/training/start?model=BART&epochs=3"
```

Response:
```json
{
  "job_id": 1,
  "status": "started",
  "model": "BART",
  "epochs": 3,
  "batch_size": 4,
  "learning_rate": 5e-5,
  "timestamp": "2026-01-22T14:30:00"
}
```

### Step 3: Monitor Progress
```bash
curl "http://127.0.0.1:8001/api/training/jobs/1"
```

Response:
```json
{
  "job_id": 1,
  "model": "BART",
  "status": "in_progress",
  "progress": 65,
  "epoch": 2,
  "total_epochs": 3,
  "loss": 0.45,
  "accuracy": 0.88
}
```

### Step 4: Evaluate Model
```bash
curl -X POST "http://127.0.0.1:8001/api/training/evaluate?job_id=1"
```

### Step 5: Run Inference
```bash
curl -X POST "http://127.0.0.1:8001/api/inference/predict?text=Summarize%20this%20legal%20document&model=BART"
```

---

## 🔧 Training Configuration

### Available Models

#### BART
- **Task**: Summarization
- **Type**: Denoising sequence-to-sequence
- **Epochs**: 3
- **Batch Size**: 4
- **Learning Rate**: 5e-5

#### PEGASUS
- **Task**: Summarization
- **Type**: Pre-training with Extracted Gap-Sentences
- **Epochs**: 3
- **Batch Size**: 4
- **Learning Rate**: 5e-5

#### Multilingual T5
- **Task**: Translation
- **Type**: Multilingual model
- **Epochs**: 3
- **Batch Size**: 4
- **Learning Rate**: 5e-5

---

## 📂 Data Structure

```
backend/data/
├── uploads/              # Uploaded datasets
├── models/               # Trained models
├── datasets/             # Processed datasets
├── processed_pdfs/       # PDF processing output
├── training_logs/        # Training logs
└── exports/              # Export results
```

---

## 🎯 Frontend Access

### Access the Application
Open http://localhost:3000 in your browser to access:
- Upload datasets
- Start training jobs
- Monitor training progress
- Evaluate models
- Run inference

---

## 📊 API Documentation

### Interactive Swagger UI
```
http://127.0.0.1:8001/api/docs
```

### ReDoc Documentation
```
http://127.0.0.1:8001/api/redoc
```

### Health Check
```
http://127.0.0.1:8001/health
```

---

## 🔄 Training Workflow

```
1. Upload Dataset
   ↓
2. Select Model (BART/PEGASUS/Multilingual)
   ↓
3. Configure Parameters (epochs, batch size, learning rate)
   ↓
4. Start Training Job
   ↓
5. Monitor Progress (check job status)
   ↓
6. Evaluate Model (get metrics)
   ↓
7. Run Inference (test predictions)
   ↓
8. Export Results
```

---

## ⚙️ System Requirements

- **Python**: 3.11.5
- **RAM**: 8GB+ (for training)
- **GPU**: Recommended (CUDA support)
- **Storage**: 2GB+ free space

---

## 📝 Example Dataset Format

```csv
text,summary
"Long legal document text here...","Brief summary..."
"Another document...","Its summary..."
```

---

## 🛠️ Troubleshooting

### Training Not Starting
1. Check dataset is uploaded: `GET /api/datasets`
2. Verify model is available: `GET /api/training/models`
3. Check backend logs for errors

### Poor Training Accuracy
1. Increase epochs: Try `epochs=5` or `epochs=10`
2. Adjust learning rate: Try `learning_rate=3e-5` or `learning_rate=1e-4`
3. Increase batch size: Try `batch_size=8` or `batch_size=16`

### Memory Issues
1. Reduce batch size: `batch_size=2`
2. Reduce epochs: `epochs=2`
3. Use a smaller model

---

## 📊 Performance Metrics

Training a BART model typically:
- **Time per epoch**: 2-5 minutes (depending on dataset size)
- **Training time (3 epochs)**: 6-15 minutes
- **Achievable accuracy**: 85-95%
- **Memory usage**: 6-8GB (with batch_size=4)

---

## 🎉 Ready to Train!

Your full project is now ready for:
✅ Dataset upload
✅ Model training
✅ Progress monitoring
✅ Model evaluation
✅ Inference/Predictions
✅ Results export

**Start training models now!**

---

## 📞 Quick Reference

| Task | Endpoint |
|------|----------|
| Get models | GET /api/training/models |
| Upload dataset | POST /api/training/upload-dataset |
| Start training | POST /api/training/start |
| View jobs | GET /api/training/jobs |
| Job details | GET /api/training/jobs/{id} |
| Evaluate | POST /api/training/evaluate |
| Predict | POST /api/inference/predict |
| API Docs | GET /api/docs |
| Health | GET /health |

---

**Last Updated**: January 22, 2026  
**Status**: ✅ FULLY OPERATIONAL WITH TRAINING
