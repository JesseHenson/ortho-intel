---
description: 
globs: 
alwaysApply: false
---
# Streamlit UI Development Rules

## **UI Consistency Standards**

### **Page Configuration Preservation**
- **Never modify `st.set_page_config()` during restructuring**
- **Preserve page title, icon, layout, and sidebar state**
- **Maintain exact configuration parameters**

```python
# ✅ DO: Preserve exact page config
st.set_page_config(
    page_title="Orthopedic Intelligence - Opportunity Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### **CSS Styling Rules**
- **Preserve all custom CSS in `st.markdown()` blocks**
- **Maintain exact color schemes and gradients**
- **Keep all CSS class names and properties**
- **Preserve responsive design and dark mode adaptations**

### **Component Hierarchy**
- **Maintain exact Streamlit component structure**
- **Preserve sidebar organization and order**
- **Keep main content layout identical**
- **Maintain tab and column structures**

## **Styling Preservation Checklist**

### **Critical Elements to Preserve**
- [ ] **Opportunity cards styling** (`.opportunity-card`)
- [ ] **Quick wins styling** (`.quick-win`)
- [ ] **Strategic investments styling** (`.strategic-investment`)
- [ ] **Executive summary styling** (`.executive-summary`)
- [ ] **Metric cards styling** (`.metric-card`)
- [ ] **Category tabs styling** (`.category-tab`)
- [ ] **Competitor profiles styling** (`.competitor-profile`)
- [ ] **Dark mode adaptations** (`@media (prefers-color-scheme: dark)`)

### **Interactive Elements**
- [ ] **Form inputs (text_input, multiselect, selectbox)**
- [ ] **Button styling and behavior**
- [ ] **Sidebar controls and organization**
- [ ] **Tab navigation and content**
- [ ] **Chart and visualization rendering**

## **Development Patterns**

### **Entry Point Pattern**
```python
# ✅ DO: Use thin wrapper for restructured apps
#!/usr/bin/env python3
"""
Main entry point for Orthopedic Intelligence Platform
Imports from restructured frontend components
"""

from src.frontend.streamlit_app_opportunity import main

if __name__ == "__main__":
    main()
```

### **Import Management**
- **Update import paths systematically**
- **Preserve all functional imports**
- **Maintain data model imports**
- **Keep visualization library imports**

### **State Management**
- **Preserve session state usage**
- **Maintain caching decorators**
- **Keep form state handling**
- **Preserve user input persistence**

## **Visual Design Standards**

### **Color Scheme**
- **Primary gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Success gradient**: `linear-gradient(135deg, #11998e 0%, #38ef7d 100%)`
- **Warning gradient**: `linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%)`
- **Executive gradient**: `linear-gradient(135deg, #2c3e50 0%, #34495e 100%)`

### **Typography**
- **Headers**: Maintain font sizes and weights
- **Body text**: Preserve color and spacing
- **Metrics**: Keep large number styling
- **Labels**: Maintain uppercase and letter-spacing

### **Layout Standards**
- **Wide layout**: Always use `layout="wide"`
- **Sidebar**: Expanded by default
- **Cards**: Consistent padding and border-radius
- **Spacing**: Maintain margin and padding values

## **Testing Requirements**

### **Visual Regression Testing**
```python
# Test checklist for UI changes
def test_ui_preservation():
    """Verify UI elements render correctly"""
    # 1. Check page loads without errors
    # 2. Verify all CSS classes are applied
    # 3. Confirm color schemes match original
    # 4. Test responsive behavior
    # 5. Validate dark mode compatibility
    # 6. Check interactive elements work
    # 7. Verify chart rendering
    # 8. Test form submissions
```

### **Functional Testing**
- **All form inputs accept and process data correctly**
- **Sidebar controls update main content**
- **Charts render with correct data**
- **Navigation between sections works**
- **Error handling displays appropriately**

## **Common Issues and Solutions**

### **Import Path Problems**
```python
# ❌ WRONG: Broken relative imports after restructuring
from ...backend.pipelines.main_langgraph_opportunity import opportunity_graph

# ✅ CORRECT: Updated import paths
from ..backend.pipelines.main_langgraph_opportunity import opportunity_graph
```

### **CSS Not Loading**
```python
# ❌ WRONG: Missing or modified CSS
st.markdown("<style>.opportunity-card { background: blue; }</style>")

# ✅ CORRECT: Exact original CSS preserved
st.markdown("""
<style>
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
```

## **Performance Considerations**

### **Caching Strategy**
- **Preserve all `@st.cache_data` decorators**
- **Maintain cache keys and TTL values**
- **Keep expensive computation caching**
- **Preserve API call caching**

### **Loading Optimization**
- **Maintain lazy loading patterns**
- **Preserve conditional rendering**
- **Keep efficient data processing**
- **Maintain chart optimization**

## **Accessibility Standards**

### **User Experience**
- **Maintain clear navigation**
- **Preserve helpful tooltips and help text**
- **Keep consistent interaction patterns**
- **Maintain responsive design**

### **Content Organization**
- **Preserve logical content hierarchy**
- **Maintain clear section divisions**
- **Keep consistent labeling**
- **Preserve executive summary prominence**
