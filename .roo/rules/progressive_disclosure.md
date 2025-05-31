---
description:
globs:
alwaysApply: false
---
# Progressive Disclosure UI Rules

## **Core Principles**

### **Information Hierarchy**
- **Always implement three-tier disclosure**: Summary → Details → Full Analysis
- **Preserve visual hierarchy** with consistent spacing and typography
- **Use clear visual cues** for expandable content (arrows, icons, hover states)

### **State Management**
- **Track expansion state** in session state or component state
- **Maintain state consistency** across page reloads when possible
- **Provide clear feedback** for loading states during expansion

## **Accordion Implementation**

### **Component Structure**
```python
# ✅ DO: Use consistent accordion structure
def create_opportunity_accordion(opportunity_data):
    with st.expander(f"🎯 {opportunity_data['title']}", expanded=False):
        # Level 1: Summary (always visible)
        display_opportunity_summary(opportunity_data)
        
        # Level 2: Details (expandable)
        if st.button("View Details", key=f"details_{opportunity_data['id']}"):
            display_opportunity_details(opportunity_data)
            
            # Level 3: Full Analysis (nested expandable)
            if st.button("View Analysis", key=f"analysis_{opportunity_data['id']}"):
                display_full_analysis(opportunity_data)
```

### **Visual Design Standards**
- **Consistent spacing**: Use 1rem margins between sections
- **Clear visual separation**: Use borders or background colors
- **Smooth transitions**: Implement loading states for async content
- **Accessibility**: Include proper ARIA labels and keyboard navigation

## **Data Loading Patterns**

### **Lazy Loading**
- **Load summary data immediately** for initial display
- **Fetch details on demand** when user expands sections
- **Cache loaded data** to avoid repeated API calls
- **Show loading indicators** during data fetching

### **Error Handling**
```python
# ✅ DO: Graceful error handling
try:
    detailed_data = fetch_opportunity_details(opportunity_id)
    display_opportunity_details(detailed_data)
except Exception as e:
    st.error("Unable to load detailed analysis. Please try again.")
    st.info("Summary information is still available above.")
```

## **Source Citation Standards**

### **Citation Format**
- **Include source credibility indicators** (domain, date, relevance score)
- **Make citations clickable** with proper target="_blank"
- **Add hover tooltips** with source previews
- **Group citations by relevance** or topic

### **Source Display**
```python
# ✅ DO: Consistent source citation format
def display_source_citation(source):
    st.markdown(f"""
    <div class="source-citation">
        <a href="{source['url']}" target="_blank" rel="noopener">
            📄 {source['title']}
        </a>
        <span class="source-meta">
            {source['domain']} • {source['date']} • 
            <span class="credibility-{source['credibility']}">{source['credibility']}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
```

## **Performance Considerations**

### **Optimization Rules**
- **Implement virtual scrolling** for large lists of opportunities
- **Use pagination** for extensive analysis content
- **Minimize DOM updates** during expansion/collapse
- **Cache expanded content** in session state

### **Memory Management**
- **Clean up unused expanded content** after user navigation
- **Limit concurrent expanded sections** to prevent memory issues
- **Use weak references** for cached data when possible

## **Testing Requirements**

### **Accessibility Testing**
- **Test keyboard navigation** through all disclosure levels
- **Verify screen reader compatibility** with ARIA labels
- **Check color contrast** for all disclosure states
- **Test with assistive technologies**

### **Interaction Testing**
- **Test rapid expand/collapse** operations
- **Verify state persistence** across page interactions
- **Test concurrent user sessions** with different expansion states
- **Validate mobile touch interactions**

## **Common Anti-Patterns**

### **❌ DON'T: Violate Information Hierarchy**
```python
# ❌ DON'T: Show full analysis before summary
if show_analysis:
    display_full_analysis()  # Missing summary context

# ❌ DON'T: Inconsistent expansion behavior
st.expander("Details", expanded=True)  # Should default to collapsed
```

### **❌ DON'T: Poor State Management**
```python
# ❌ DON'T: Lose state on page refresh
expanded = st.checkbox("Show details")  # State not persisted

# ❌ DON'T: Conflicting expansion states
if st.button("Expand All") and st.button("Collapse All"):  # Confusing UX
```

## **Integration Guidelines**

### **With Existing Components**
- **Maintain existing color scheme** and design tokens
- **Preserve current opportunity card styling** in summary view
- **Extend rather than replace** current components
- **Follow established naming conventions**

### **With Backend APIs**
- **Design APIs for progressive loading** (summary, details, analysis endpoints)
- **Include metadata** for expansion state management
- **Handle partial data gracefully** when full analysis unavailable
- **Implement proper caching headers** for expanded content
