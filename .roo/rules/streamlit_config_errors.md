---
description:
globs:
alwaysApply: false
---
# Streamlit Configuration & Import Error Prevention

## **Critical: Streamlit set_page_config() Rules**

### ✅ DO: Always Call set_page_config() First
```python
import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="App Title",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# All other imports AFTER set_page_config
import plotly.express as px
# ... other imports
```

### ❌ DON'T: Call set_page_config() in Component Files
```python
# DON'T DO THIS in component files:
# src/frontend/components/demo_frontend.py
st.set_page_config(...)  # This will cause conflicts!
```

### ✅ DO: Comment Out Conflicting Imports in __init__.py
```python
# src/frontend/components/__init__.py
from .progressive_disclosure import *

# Comment out imports that contain st.set_page_config():
# from .demo_frontend import *  # Contains st.set_page_config()
```

## **Critical: Import Structure Rules**

### ✅ DO: Use Proper Import Patterns for Streamlit Apps
```python
# For files that may be run directly, use try/except pattern:
import sys
import os

# Add project root to path for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Try relative imports first (when run through launcher)
    from ..backend.pipelines.main_langgraph_opportunity import opportunity_graph
except ImportError:
    # Fall back to absolute imports (when run directly)
    from src.backend.pipelines.main_langgraph_opportunity import opportunity_graph
```

### ✅ DO: Always Run Streamlit from Project Root
```bash
# CORRECT: Run from project root using launcher
streamlit run streamlit_app_opportunity.py

# INCORRECT: Running directly from src/frontend/ causes import errors
streamlit run src/frontend/streamlit_app_opportunity.py  # DON'T DO THIS
```

## **Critical: HTML Rendering Rules**

### ✅ DO: Proper HTML Structure in st.markdown()
```python
# Use proper container structure for complex HTML
st.markdown(f"""
<div style="background: white; padding: 1rem; border-radius: 8px;">
    <h3>{title}</h3>
    <p>{description}</p>
</div>
""", unsafe_allow_html=True)
```

### ❌ DON'T: Mix HTML and Markdown Without Proper Handling
```python
# This can cause rendering issues:
st.markdown(f"""
## Markdown Header
<div>HTML content</div>
More markdown content
""")  # Missing unsafe_allow_html=True for HTML parts
```

### ✅ DO: Handle Mixed Content Properly
```python
# Separate markdown and HTML rendering:
st.markdown("## Markdown Header")  # Pure markdown
st.markdown("<div>HTML content</div>", unsafe_allow_html=True)  # HTML with flag
st.markdown("More markdown content")  # Pure markdown
```

## **Testing Protocol for Agents**

### 🤖 BEFORE Making Pipeline/Frontend Changes:
```bash
# 1. Test basic imports
python -c "from src.frontend.streamlit_app_opportunity import main; print('✅ Import successful!')"

# 2. Test progressive disclosure components
python -c "from src.frontend.components.progressive_disclosure import OpportunityCard; print('✅ Components import successful!')"

# 3. Test Streamlit app launch
streamlit run streamlit_app_opportunity.py --server.headless true --server.port 8506

# 4. Verify app accessibility
curl -f http://localhost:8506 > /dev/null && echo "✅ App running" || echo "❌ App failed"
```

### 🤖 AFTER Making Changes:
```bash
# 1. Run component tests
python -m pytest src/frontend/tests/test_progressive_disclosure_html_rendering.py -v

# 2. Test HTML rendering specifically
python -c "
from src.frontend.components.progressive_disclosure import OpportunityCard
test_opp = {'title': 'Test', 'opportunity_score': 8.0, 'category': 'Test'}
print('✅ Component creation successful!')
"

# 3. Restart Streamlit and verify
pkill -f streamlit
streamlit run streamlit_app_opportunity.py --server.port 8507
```

## **Common Error Patterns & Fixes**

### Error: "set_page_config() can only be called once"
**Cause:** Multiple files calling `st.set_page_config()`
**Fix:** 
1. Move `st.set_page_config()` to be the first command after `import streamlit as st`
2. Comment out `st.set_page_config()` in component files
3. Update `__init__.py` to exclude problematic imports

### Error: "attempted relative import with no known parent package"
**Cause:** Running Streamlit app directly from subdirectory
**Fix:**
1. Always run from project root: `streamlit run streamlit_app_opportunity.py`
2. Add sys.path handling for absolute imports
3. Use try/except pattern for import fallbacks

### Error: HTML showing as raw text instead of rendered
**Cause:** Missing `unsafe_allow_html=True` or malformed HTML structure
**Fix:**
1. Add `unsafe_allow_html=True` to all `st.markdown()` calls with HTML
2. Ensure proper HTML structure with opening/closing tags
3. Separate pure markdown from HTML content

### Error: "Mock object does not support context manager protocol"
**Cause:** Incomplete mocking of Streamlit components in tests
**Fix:**
```python
# Proper context manager mocking:
mock_col = Mock()
mock_col.__enter__ = Mock(return_value=mock_col)
mock_col.__exit__ = Mock(return_value=None)
mock_st.columns = Mock(return_value=[mock_col])
```

## **File Organization Rules**

### ✅ DO: Proper Project Structure
```
project_root/
├── streamlit_app_opportunity.py  # Launcher (contains set_page_config)
├── src/frontend/
│   ├── streamlit_app_opportunity.py  # Main app (no set_page_config)
│   └── components/
│       ├── __init__.py  # Careful with imports
│       └── progressive_disclosure.py  # No set_page_config
```

### ✅ DO: Update README.md with Proper Instructions
```markdown
## Running the Application

**IMPORTANT: Always run from project root:**
```bash
streamlit run streamlit_app_opportunity.py
```

**❌ DO NOT run directly from src/frontend/:**
```bash
streamlit run src/frontend/streamlit_app_opportunity.py  # Causes import errors
```

## **Prevention Checklist**

- [ ] `st.set_page_config()` is the first Streamlit command
- [ ] No `st.set_page_config()` in component files
- [ ] All HTML uses `unsafe_allow_html=True`
- [ ] Imports use try/except pattern for flexibility
- [ ] Tests properly mock Streamlit context managers
- [ ] App runs from project root using launcher
- [ ] README.md has correct run instructions

## **Emergency Fixes**

### Quick HTML Rendering Fix:
```python
# Replace problematic HTML rendering:
st.markdown(html_content, unsafe_allow_html=True)

# With safer alternative:
st.html(html_content)  # If available in Streamlit version
# OR
st.components.v1.html(html_content)  # For complex HTML
```

### Quick Import Fix:
```python
# Add to top of problematic file:
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
```

---

**Related Rules:**
- [pydantic_validation.md](mdc:.roo/rules/pydantic_validation.md) - Model validation patterns
- [backend_organization.md](mdc:.roo/rules/backend_organization.md) - Backend structure
- [dev_workflow.md](mdc:.roo/rules/dev_workflow.md) - Development workflow
