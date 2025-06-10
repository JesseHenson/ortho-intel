# Orthopedic Intelligence Platform

A competitive intelligence platform for orthopedic medical device companies, providing AI-powered market analysis and strategic opportunity identification.

## 🚀 Quick Start

### Project Structure

```
ortho-intel/
├── src/
│   ├── frontend-react/         # React + Vite frontend
│   └── backend/                # FastAPI backend
│       ├── api/
│       ├── core/
│       ├── pipelines/
│       └── requirements.txt
├── README.md
└── ...
```

---

## 🔧 Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd ortho-intel
```

---

### 2. Backend Setup (FastAPI)

```bash
cd src/backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### Create a `.env` file in `src/backend/` with:

```
TAVILY_API_KEY=your-tavily-api-key
OPENAI_API_KEY=your-openai-api-key
```

#### Start the backend server:

```bash
uvicorn api.fastapi_server:app --reload
```
The API will be available at [http://localhost:8000](http://localhost:8000).

---

### 3. Frontend Setup (React + Vite)

```bash
cd ../frontend-react
npm install
npm run dev
```
The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## 🎯 Features & Functionality

### Backend (FastAPI)
- **AI-powered competitive analysis** for orthopedic device companies
- **Progressive disclosure API**: Summary, Detail, and Full Analysis endpoints for opportunities
- **Source credibility scoring** and evidence tracking
- **Real-time streaming** of analysis results
- **Market opportunity identification** and clinical gap analysis
- **Competitive landscape and feature comparison**
- **Executive summary and strategic recommendations**
- **PDF export support (planned)**
- **API endpoints for summary, details, full analysis, category breakdown, sources, methodology, traceability, and quality report**
- **Support for multiple competitors and focus areas**
- **Robust error handling and partial result support**

### Frontend (React + Vite)
- **Modern dashboard UI for business users**
- **Feature comparison tables and competitive gap visualization**
- **Progressive disclosure of opportunity data (summary, detail, full)**
- **Interactive competitor and focus area selection**
- **Market importance and gap severity visualization**
- **Executive summary and actionable recommendations display**
- **Export and reporting tools (PDF export planned)**
- **Responsive design for desktop and tablet**

---

## 🏗️ Architecture

### Frontend Components
- **Progressive Disclosure UI**: `src/frontend/components/progressive_disclosure.py`
- **Main Application**: `src/frontend/streamlit_app_opportunity.py`
- **Launcher Script**: `streamlit_app_opportunity.py` (root level)

### Backend Pipeline
- **LangGraph Opportunity Pipeline**: `src/backend/pipelines/main_langgraph_opportunity.py`
- **Data Models**: `src/backend/core/opportunity_data_models.py`
- **Source Management**: `src/backend/core/source_models.py`

### Testing
- **Progressive Disclosure Tests**: `src/frontend/tests/test_progressive_disclosure_components.py`
- **Model Validation Tests**: `src/backend/tests/test_category_opportunity_validation.py`
- **Integration Tests**: `src/frontend/tests/test_progressive_disclosure_integration.py`

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest src/frontend/tests/ -v
python -m pytest src/backend/tests/ -v

# Run validation tests (recommended before deployment)
python -c "from src.backend.tests.test_category_opportunity_validation import test_all_pydantic_models_validation; test_all_pydantic_models_validation()"
```

## 📊 Usage

1. Start both backend and frontend as described above.
2. Configure analysis in the frontend:
   - Enter client name (optional)
   - Select competitors (Quick Select or Custom Input)
   - Choose focus area (spine_fusion, joint_replacement, etc.)
   - Select analysis priority
3. Run analysis and explore results using progressive disclosure:
   - Summary Cards: Quick opportunity overview
   - View Details: Implementation information
   - Full Analysis: Complete analysis with sources

## 🎯 Features

### Progressive Disclosure Intelligence
- **Three-tier information architecture**: Summary → Details → Full Analysis
- **Source credibility assessment**: 🟢 High, 🟡 Medium, 🔴 Low credibility indicators
- **Real-time competitive analysis** with AI-powered insights
- **Executive-ready reports** with actionable recommendations

### Advanced Analytics
- **Opportunity matrix visualization** (Impact vs Implementation Difficulty)
- **Competitive landscape mapping** with strategic positioning
- **Market expansion opportunities** across multiple segments
- **Value-based pricing recommendations**

### Data Sources & Credibility
- **High Credibility**: PubMed, FDA, Reuters, Bloomberg, WSJ, Nature, NEJM
- **Medium Credibility**: Forbes, CNN, BBC, Medscape, MedTechDive
- **Transparent source attribution** with clickable citations

## 🧪 Testing

Run backend tests:
```bash
cd src/backend
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the development guidelines above
4. Run tests before submitting
5. Submit a pull request