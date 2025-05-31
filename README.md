# Orthopedic Intelligence Platform

A competitive intelligence platform for orthopedic medical device companies, providing AI-powered market analysis and strategic opportunity identification.

## 🚀 Quick Start

### Running the Application

**IMPORTANT: Always run the Streamlit app from the project root using the launcher script:**

```bash
# Correct way to run the application
streamlit run streamlit_app_opportunity.py

# Alternative using Python module
python -m streamlit run streamlit_app_opportunity.py
```

**❌ DO NOT run the app directly from the src/frontend/ directory:**
```bash
# This will cause import errors:
streamlit run src/frontend/streamlit_app_opportunity.py  # DON'T DO THIS
```

### Project Structure

```
ortho-intel/
├── streamlit_app_opportunity.py          # 🎯 MAIN LAUNCHER - Use this file!
├── src/
│   ├── frontend/
│   │   ├── streamlit_app_opportunity.py  # Actual frontend code
│   │   └── components/
│   │       └── progressive_disclosure.py
│   └── backend/
│       ├── pipelines/
│       └── core/
├── README.md                             # This file
└── requirements.txt
```

The root-level `streamlit_app_opportunity.py` is a launcher that properly sets up the Python path and imports the actual application from `src/frontend/streamlit_app_opportunity.py`.

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ortho-intel
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

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

## 🔧 Development

### Adding New Features
1. Follow the progressive disclosure pattern for UI components
2. Use the validation patterns in `.cursor/rules/pydantic_validation.mdc`
3. Always test model creation before pipeline changes
4. Run validation tests: `python -m pytest src/backend/tests/test_category_opportunity_validation.py -v`

### Common Issues & Solutions

#### Import Errors
**Problem**: `ImportError: attempted relative import with no known parent package`
**Solution**: Always run from project root using `streamlit run streamlit_app_opportunity.py`

#### Streamlit Configuration Errors
**Problem**: `set_page_config() can only be called once per app page`
**Solution**: Ensure `st.set_page_config()` is the first Streamlit command (already fixed in current version)

#### Model Validation Errors
**Problem**: `Field required [type=missing, input_value={...}]`
**Solution**: Use safe model creation patterns documented in `.cursor/rules/pydantic_validation.mdc`

## 📊 Usage

1. **Start the application:**
   ```bash
   streamlit run streamlit_app_opportunity.py
   ```

2. **Configure analysis:**
   - Enter client name (optional)
   - Select competitors (Quick Select or Custom Input)
   - Choose focus area (spine_fusion, joint_replacement, etc.)
   - Select analysis priority

3. **Run analysis:**
   - Click "🚀 Run Opportunity Analysis"
   - Wait for AI-powered analysis to complete
   - Explore results using progressive disclosure

4. **Navigate results:**
   - **Summary Cards**: Quick opportunity overview
   - **View Details**: Implementation information
   - **Full Analysis**: Complete analysis with sources

## 🌟 Value Proposition

### vs. Regular ChatGPT
- **Specialized medical device intelligence** vs. generic AI responses
- **Source credibility assessment** with domain-based scoring
- **Real-time research integration** vs. static knowledge cutoff
- **Progressive disclosure UX** for efficient information consumption
- **Executive-ready formatting** with actionable recommendations

### Key Differentiators
- **Advanced source credibility system** (🟢🟡🔴⚪)
- **Three-tier progressive disclosure** architecture
- **Medical device market specialization**
- **Competitive gap analysis** with strategic recommendations
- **Outcome-focused insights** for business decision making

## 🔑 API Keys

Configure the following environment variables in your `.env` file:

```bash
# Required for AI analysis
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key  # For research-backed analysis
OPENAI_API_KEY=your_openai_key

# Optional for enhanced research
TAVILY_API_KEY=your_tavily_key
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the development guidelines above
4. Run tests before submitting
5. Submit a pull request

---

**Remember**: Always use `streamlit run streamlit_app_opportunity.py` from the project root to avoid import issues! 