# Orthopedic Competitive Intelligence Platform

AI-powered competitive intelligence for orthopedic device manufacturers, providing strategic insights and market opportunities through automated analysis.

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   ./run_setup.sh
   ```

2. **Configure API Keys**
   Edit `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key
   ```

3. **Run the Application**
   ```bash
   # Start API server
   python fastapi_server.py
   
   # Start frontend (in another terminal)
   streamlit run streamlit_app_opportunity.py
   ```

4. **Access the App**
   - Frontend: http://localhost:8501
   - API: http://localhost:8000

## 📁 Project Structure

```
ortho-intel/
├── src/
│   ├── backend/
│   │   ├── core/           # Data models and business logic
│   │   │   ├── data_models.py
│   │   │   └── opportunity_data_models.py
│   │   ├── pipelines/      # LangGraph workflows
│   │   │   ├── main_langgraph.py
│   │   │   ├── main_langgraph_opportunity.py
│   │   │   └── main_langgraph_opportunity_enhanced.py
│   │   ├── api/            # FastAPI server
│   │   │   └── fastapi_server.py
│   │   └── utils/          # Utilities and demo data
│   │       └── demo_data.py
│   └── frontend/
│       ├── components/     # Reusable UI components
│       │   ├── demo_frontend.py
│       │   ├── demo_frontend_adapter.py
│       │   ├── demo_frontend_enhanced.py
│       │   └── demo_frontend_fixed.py
│       ├── auth/           # Authentication components
│       │   └── streamlit_auth.py
│       ├── streamlit_app_opportunity.py  # Main opportunity-focused UI
│       ├── streamlit_app.py              # Original UI
│       └── streamlit_app_opportunity_enhanced.py
├── tests/
│   ├── backend/            # Backend tests
│   │   ├── test_baseline.py
│   │   ├── test_dataset.py
│   │   └── test_integration.py
│   ├── frontend/           # Frontend tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── archive/                # Archived legacy files
├── fastapi_server.py       # Main API entry point
├── streamlit_app_opportunity.py  # Main frontend entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
└── run_setup.sh           # Setup script
```

## 🔧 Development

### Running Tests
```bash
# Backend tests
python -m pytest tests/backend/ -v

# All tests
python -m pytest tests/ -v
```

### Key Components

- **Backend Core**: Data models and business logic in `src/backend/core/`
- **Pipelines**: LangGraph workflows for competitive analysis in `src/backend/pipelines/`
- **API**: FastAPI server providing REST endpoints in `src/backend/api/`
- **Frontend**: Streamlit applications and UI components in `src/frontend/`

### Test Data
The system includes established test competitors:
- Stryker Spine
- Zimmer Biomet  
- Orthofix

## 🎯 Features

- **Opportunity-First Analysis**: Prioritizes actionable market opportunities
- **Multi-Category Support**: Works across orthopedic device categories
- **Executive-Ready Insights**: Formatted for business decision-making
- **Real-Time Research**: Powered by Tavily API for current market data
- **Interactive UI**: Streamlit-based interface for easy exploration

## 📊 API Endpoints

- `GET /health` - Health check
- `POST /analyze-gaps-sync` - Synchronous competitive analysis
- `POST /analyze-gaps` - Asynchronous competitive analysis

## 🔑 Environment Variables

Required API keys:
- `OPENAI_API_KEY` - OpenAI API access
- `TAVILY_API_KEY` - Tavily search API access

## 📈 Usage

1. Select competitors from the dropdown or enter custom ones
2. Choose focus area (e.g., spine_fusion, joint_replacement)
3. Run analysis to get:
   - Clinical gaps in competitor offerings
   - Market opportunities
   - Strategic recommendations
   - Evidence-backed insights

## 🛠️ Installation

### Using pip
```bash
pip install -e .
```

### Using setup.py
```bash
python setup.py install
```

## 📝 License

This project is proprietary software for orthopedic device manufacturers.

## 🤝 Contributing

1. Create feature branch from main
2. Make changes following project structure
3. Run tests to ensure functionality
4. Submit pull request

## 📞 Support

For technical support or questions about the competitive intelligence platform, please contact the development team. 