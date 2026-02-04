# Graph RAG

## Install
### System Environment
- [python 3.11](https://www.python.org/downloads/)
- [ollama](https://ollama.com/) (model: qwen3:8b)
- [nodejs](https://nodejs.org/zh-tw/download)

### ASR Model
**pyannote/speaker-diarization**
```
pip install huggingface_hub
huggingface-cli login
huggingface-cli download pyannote/speaker-diarization --local-dir your/model/path
```
**openai/whisper-large-v3**
```
huggingface-cli download openai/whisper-large-v3 --local-dir your/model/path
```
### Backend Environment
```
cd backend
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
```
### Frontend Environment
```
npm install
```

## Run
**Two terminals are required and make sure the Ollama AI server is running.**

**Frontend:**
```
cd frontend
npm run dev
```

**Backend**
```
cd backend
python main.py
```