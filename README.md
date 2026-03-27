
An AI-powered country information agent built with LangGraph and FastAPI





## Run Locally

# Clone and enter directory
cd country-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run
uvicorn app.main:app --reload --port 8000
