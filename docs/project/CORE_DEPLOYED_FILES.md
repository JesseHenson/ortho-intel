# Core Deployed Files Documentation

**Created**: 2025-01-27  
**Purpose**: Document all files essential for production deployment  
**Status**: ✅ VERIFIED - These files must be preserved during cleanup

---

## 🎯 PRODUCTION FRONTEND

### **Primary Frontend (PRODUCTION)**
- **`streamlit_app_opportunity.py`** - ✅ CRITICAL
  - Current production deployment
  - Opportunity-first competitive intelligence interface
  - Executive-ready design with client name input
  - Imports: `main_langgraph_opportunity`, `opportunity_data_models`

### **Authentication**
- **`streamlit_auth.py`** - ✅ CRITICAL
  - Password protection for production deployment
  - Used by streamlit apps for access control

---

## 🔧 PRODUCTION BACKEND

### **Core Pipeline**
- **`main_langgraph_opportunity.py`** - ✅ CRITICAL
  - Production LangGraph pipeline
  - Opportunity-first analysis workflow
  - 6-node pipeline: detect_category → research → analyze → synthesize

### **Data Models**
- **`data_models.py`** - ✅ CRITICAL
  - Core data structures and schemas
  - GraphState, SearchTemplates, AnalysisProcessor
  - CategoryRouter for device category detection
  - 4 device categories with 32 competitors

- **`opportunity_data_models.py`** - ✅ CRITICAL
  - Opportunity-specific data models
  - StrategicOpportunity, CategoryOpportunity, ExecutiveSummary
  - OpportunityTransformer, OpportunityRanker classes

### **API Server**
- **`fastapi_server.py`** - ✅ CRITICAL
  - REST API for external integrations
  - Background task processing
  - Health check endpoints

### **Utilities**
- **`demo_data.py`** - ✅ CRITICAL
  - Demo scenarios and fallback data
  - 8 demo scenarios across 4 device categories
  - Used when live analysis fails

- **`test_dataset.py`** - ✅ CRITICAL
  - Test data for validation
  - Used by testing framework
  - Contains competitor test data

---

## 📋 CONFIGURATION & SETUP

### **Dependencies**
- **`requirements.txt`** - ✅ CRITICAL
  - Python package dependencies
  - LangGraph, Streamlit, FastAPI, OpenAI, etc.

- **`setup.py`** - ✅ CRITICAL
  - Package installation configuration
  - Project metadata and dependencies

### **Environment & Config**
- **`.env`** - ✅ CRITICAL (if exists)
  - API keys and environment variables
  - TAVILY_API_KEY, OPENAI_API_KEY

- **`.env.example`** - ✅ IMPORTANT
  - Template for environment setup
  - Documentation for required keys

- **`.taskmasterconfig`** - ✅ IMPORTANT
  - Task Master configuration
  - AI model settings

### **Git Configuration**
- **`.gitignore`** - ✅ IMPORTANT
  - Prevents committing sensitive files
  - Excludes venv, __pycache__, .env

---

## 📁 ESSENTIAL DIRECTORIES

### **Task Management**
- **`tasks/`** - ✅ CRITICAL
  - `tasks.json` - Current task tracking
  - Task Master project management

### **Scripts**
- **`scripts/`** - ✅ IMPORTANT
  - `prd.txt` - Product requirements
  - Setup and deployment scripts

### **Documentation**
- **`CURSOR_CONTEXT.md`** - ✅ IMPORTANT
  - Project context for AI agents
  - Development guidelines

- **`PROJECT_HANDOFF.md`** - ✅ IMPORTANT
  - Comprehensive project documentation
  - Architecture and deployment info

---

## 🧪 ESSENTIAL TESTS

### **Core Testing**
- **`tests/test_category_detection.py`** - ✅ IMPORTANT
  - Category router validation
  - Device category detection tests

- **`tests/test_backward_compatibility.py`** - ✅ IMPORTANT
  - Ensures existing functionality preserved
  - Spine fusion compatibility tests

- **`tests/test_performance.py`** - ✅ IMPORTANT
  - Performance benchmarks
  - System performance validation

---

## ⚠️ FILES TO PRESERVE BUT EVALUATE

### **Alternative Versions (Keep for Reference)**
- **`streamlit_app.py`** - Original version (keep as reference)
- **`main_langgraph.py`** - Original pipeline (keep as reference)

### **Enhanced Versions (Evaluate Need)**
- **`streamlit_app_opportunity_enhanced.py`** - Enhanced version
- **`main_langgraph_opportunity_enhanced.py`** - Enhanced pipeline

---

## 🗑️ SAFE TO REMOVE CATEGORIES

### **Backup Files**
- `*_BACKUP.py` files
- `rollback_migration.sh`

### **Legacy Test Files**
- `test_opportunity_migration.py`
- `test_visual_preservation.py`
- `test_enhanced_frontend.py`
- `test_frontend_validation.py`

### **Development Artifacts**
- `debug_opportunity_data.py`
- `debug_opportunity_result.json`
- Performance baseline files

### **Legacy Documentation**
- `FRONTEND_ENHANCEMENT_TASKS.md`
- `VISUAL_COMPARISON_RESULTS.md`
- `FRONTEND_MIGRATION_PLAN.md`
- Completed project documentation

---

## ✅ VERIFICATION CHECKLIST

- [ ] Production frontend starts: `streamlit run streamlit_app_opportunity.py`
- [ ] Backend imports work: `from main_langgraph_opportunity import opportunity_graph`
- [ ] Data models import: `from data_models import GraphState`
- [ ] API server starts: `python fastapi_server.py`
- [ ] Tests pass: `python -m pytest tests/`
- [ ] Environment loads: API keys accessible

---

**Total Core Files**: 15 critical + 8 important = 23 essential files
**Safe to Remove**: ~40+ legacy/backup/development files 