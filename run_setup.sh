#!/bin/bash

echo "🚀 Setting up Orthopedic Competitive Intelligence System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment (Linux/Mac)
echo "🔧 Activating virtual environment..."
source venv/bin/activate || venv\Scripts\activate.bat

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys!"
else
    echo "✅ .env file already exists"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run FastAPI server: python fastapi_server.py"
echo "3. Run Streamlit frontend: streamlit run streamlit_app_opportunity.py"
echo ""
echo "🔗 Access the app at: http://localhost:8501"
echo ""
echo "📁 Project structure:"
echo "  src/backend/    - Backend components (pipelines, API, data models)"
echo "  src/frontend/   - Frontend components (Streamlit apps, UI components)"
echo "  tests/          - Test files organized by component type"