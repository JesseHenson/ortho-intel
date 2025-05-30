---
description: 
globs: 
alwaysApply: false
---
# UI Preservation Rules

## **Core Principle: Visual Consistency**
- **NEVER modify UI styling, layout, or visual appearance** during code restructuring tasks
- **Preserve exact CSS styling, colors, fonts, and spacing** when moving or refactoring frontend code
- **Maintain identical user experience** regardless of backend changes

## **Code Restructuring Guidelines**

### **Import Path Updates Only**
- When moving frontend files, **ONLY update import paths**
- **DO NOT modify any UI components, styling, or layout logic**
- **Preserve all CSS classes, inline styles, and Streamlit configurations**

### **Entry Point Preservation**
- **Keep main entry points (like `streamlit_app_opportunity.py`) as thin wrappers**
- **Import and call original functionality without modification**
- **Preserve original file structure in user-facing components**

### **CSS and Styling Rules**
- **NEVER remove or modify existing CSS classes**
- **Preserve all `st.markdown()` styling blocks exactly**
- **Maintain color schemes, gradients, and visual hierarchy**
- **Keep all custom CSS variables and media queries**

## **Testing Requirements**

### **Visual Regression Testing**
- **Compare UI before and after restructuring**
- **Verify all styling elements render identically**
- **Test responsive behavior and dark mode compatibility**

### **Functional Testing**
- **Ensure all interactive elements work identically**
- **Verify form inputs, buttons, and navigation**
- **Test data visualization and chart rendering**

## **Common Anti-Patterns to Avoid**

```python
# ❌ DON'T: Modify styling during restructuring
st.markdown("""
<style>
    .opportunity-card {
        background: #new-color;  /* Changed during move */
    }
</style>
""")

# ✅ DO: Preserve exact styling
st.markdown("""
<style>
    .opportunity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        /* ... exact original styling ... */
    }
</style>
""")
```

## **Restructuring Checklist**

- [ ] **Import paths updated correctly**
- [ ] **All CSS styling preserved exactly**
- [ ] **Page configuration unchanged**
- [ ] **Component hierarchy maintained**
- [ ] **Interactive elements function identically**
- [ ] **Visual appearance matches original**
- [ ] **Responsive behavior preserved**
- [ ] **Dark mode compatibility maintained**

## **Documentation Requirements**

- **Document any UI-related changes separately from restructuring**
- **Note preserved styling elements in commit messages**
- **Reference original UI files when creating new entry points**
- **Maintain visual design documentation**

## **Emergency Rollback Plan**

- **Keep original UI files as reference during restructuring**
- **Create visual comparison screenshots before changes**
- **Maintain backup of working UI state**
- **Document exact steps to restore original appearance**
