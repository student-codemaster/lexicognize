# LexiCognize Training Interface Guide

## 🎯 Quick Start

Your complete training platform is now **running and ready to use!**

### Access Points:

1. **Training Interface** (Recommended)
   - URL: http://localhost:3000/training.html
   - Visual dashboard for training, uploads, and predictions
   - Real-time metrics and progress tracking

2. **API Documentation** (For developers)
   - URL: http://127.0.0.1:8001/api/docs
   - Interactive Swagger UI
   - Test API endpoints directly

3. **Root API**
   - URL: http://127.0.0.1:8001
   - Health check: Returns API status

---

## 📊 Training Interface Features

### Start Training
1. Select a model:
   - **BART** - Abstractive summarization
   - **PEGASUS** - Summarization optimized
   - **Multilingual T5** - Multilingual translation
2. Configure parameters:
   - Epochs (1-20)
   - Batch size (1-64)
   - Learning rate
3. Click "🚀 Start Training"

### Upload Dataset
1. Prepare your dataset (CSV or JSON format)
2. Give it a descriptive name
3. Click "📤 Upload Dataset"
4. Your data is now ready for training

### Make Predictions
1. Enter legal text to process
2. Select the model to use
3. Click "⚡ Predict"
4. View results instantly

### Monitor Progress
- Automatic refresh every 10 seconds
- View current epoch, loss, and accuracy
- Track training progress with visual bar
- Check job status in real-time

---

## 🔌 API Endpoints Available

### Training Management
```
GET  /api/training/models
     → List all available models

POST /api/training/start
     → Start a new training job
     Params: model, epochs, batch_size, learning_rate

GET  /api/training/jobs
     → List all training jobs

GET  /api/training/jobs/{job_id}
     → Get specific job details and status

POST /api/training/upload-dataset
     → Upload training dataset (multipart form)
```

### Inference & Evaluation
```
POST /api/inference/predict
     → Make predictions on new data
     Params: text, model

POST /api/training/evaluate
     → Evaluate model performance
     Params: job_id, test_data

GET  /api/datasets
     → List uploaded datasets
```

---

## 📝 Example Workflows

### Workflow 1: Train BART for Summarization
```
1. Go to training.html
2. Select "BART" model
3. Set epochs to 5
4. Upload your legal documents dataset
5. Click "🚀 Start Training"
6. Monitor progress via the dashboard
7. Once complete, use predictions section to test
```

### Workflow 2: Multilingual Translation
```
1. Upload translated document pairs (source/target)
2. Select "Multilingual T5"
3. Set appropriate hyperparameters
4. Start training
5. Test with multilingual text samples
```

### Workflow 3: Direct API Call (cURL)
```bash
# Start training
curl -X POST "http://127.0.0.1:8001/api/training/start?model=BART&epochs=3&batch_size=4&learning_rate=5e-5"

# Get job status
curl "http://127.0.0.1:8001/api/training/jobs/1"

# Make prediction
curl -X POST "http://127.0.0.1:8001/api/inference/predict?text=Legal text here&model=BART"
```

---

## 🛠️ Troubleshooting

### Can't Access Training Interface?
- Ensure frontend server is running (see terminal output: "✓ Frontend server running")
- Check URL: http://localhost:3000/training.html
- Verify port 3000 is not blocked

### Backend API Not Responding?
- Check backend server status: http://127.0.0.1:8001
- Verify port 8001 is available
- Look for error messages in backend terminal

### Training Job Not Starting?
- Check API response for error details
- Ensure model name is correct (BART, PEGASUS, or Multilingual)
- Verify dataset is uploaded first

### CORS Errors?
- Frontend is configured to access http://127.0.0.1:8001
- Backend CORS is enabled for localhost
- Check browser console for detailed error messages

---

## 📦 Current System Status

**Backend Server:**
- Status: ✅ Running
- Port: 8001
- Address: 127.0.0.1:8001
- Models: BART, PEGASUS, Multilingual T5
- Database: SQLite (legal_models.db)

**Frontend Server:**
- Status: ✅ Running
- Port: 3000
- Address: localhost:3000
- Files: Static React components

**Training Capabilities:**
- ✅ Model selection
- ✅ Dataset upload
- ✅ Training job management
- ✅ Real-time monitoring
- ✅ Inference/predictions
- ✅ Model evaluation

---

## 🚀 Next Steps

1. **Try the Interface**
   - Open http://localhost:3000/training.html
   - Start with a small test dataset

2. **Explore the API**
   - Check http://127.0.0.1:8001/api/docs
   - Try test requests in Swagger UI

3. **Create Your Dataset**
   - Prepare CSV or JSON files
   - Format: {text, summary} or {source, target}
   - Upload via the interface

4. **Monitor & Iterate**
   - Track training metrics
   - Adjust hyperparameters
   - Evaluate model performance

---

## 📞 Support

For detailed API information, check:
- API Swagger Docs: http://127.0.0.1:8001/api/docs
- Project README: See README.md in root directory
- Backend Logs: Check terminal output for error messages

---

**Your LexiCognize training platform is ready!** 🎉

Start at: **http://localhost:3000/training.html**
