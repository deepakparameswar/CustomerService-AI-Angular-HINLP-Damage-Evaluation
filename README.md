add the following properties inside agenticapp .env file

GROQ_API_KEY=
LANGCHAIN_API_KEY=
TAVILY_API_KEY=
HF_TOKEN=

required python vesion: 3.12

# to run the application run the bellow cmd from fastapi-backend dir
- > uvicorn main:app --host 0.0.0.0 --port 8000

./venv/Scripts/Activate.ps1
python e:\CustomerService-AI-Angular-HINLP-Damage-Evaluation\fastapi-backend\agentapp\issueRagTraining.py

pip install -r fastapi-backend/requirements.txt