---
description:
globs:
alwaysApply: false
---
# Pydantic Validation Rules

## **Required Field Validation**
- **Always include all required fields** when creating Pydantic model instances
- **Check model definitions** for required fields before instantiation
- **Use model validation tests** to catch missing field errors early

## **Model Creation Patterns**

### ✅ DO: Include All Required Fields
```python
# Check the model definition first
class CategoryOpportunity(ProgressiveDisclosureModel):
    id: Union[int, str] = Field(description="Unique identifier")  # REQUIRED
    opportunity: str = Field(description="Opportunity name")      # REQUIRED
    category_type: str = Field(description="Category type")       # REQUIRED
    # ... other fields

# Create with all required fields
category_opp = CategoryOpportunity(
    id=1,
    opportunity="Test Opportunity",
    category_type="brand",
    current_gap="Test gap",
    recommendation="Test recommendation",
    implementation="Test implementation",
    timeline="Test timeline",
    investment="Test investment"
)
```

### ❌ DON'T: Create Models Without Required Fields
```python
# This will cause ValidationError
category_opp = CategoryOpportunity(
    opportunity="Test Opportunity",
    current_gap="Test gap",
    # Missing: id and category_type (required fields)
)
```

## **Round-Trip Conversion Testing**
- **Always test model_dump() and recreation** for models used in state management
- **Validate that dict conversion preserves all required fields**

### ✅ DO: Test Round-Trip Conversion
```python
def test_model_round_trip():
    # Create model
    original = CategoryOpportunity(id=1, opportunity="Test", category_type="test", ...)
    
    # Convert to dict (simulating state storage)
    model_dict = original.model_dump()
    
    # Recreate from dict (simulating retrieval)
    recreated = CategoryOpportunity(**model_dict)
    
    # Verify key fields match
    assert recreated.id == original.id
    assert recreated.category_type == original.category_type
```

## **Pipeline Model Creation**
- **Use consistent ID schemes** for different model types
- **Include category_type or similar discriminator fields** for polymorphic models
- **Validate models immediately after creation** in pipeline methods

### ✅ DO: Consistent Pipeline Model Creation
```python
def _generate_brand_opportunities(self, competitors, device_category):
    opportunities = [
        CategoryOpportunity(
            id=1001,  # Use consistent ID ranges (1000s for brand)
            opportunity="Brand Opportunity",
            category_type="brand",  # Always include discriminator
            # ... other required fields
        )
    ]
    return opportunities
```

## **Error Prevention Strategies**

### **1. Model Definition Review**
- **Check for required fields** (no default values) before using models
- **Document required vs optional fields** in model docstrings
- **Use type hints consistently** for Union types and optional fields

### **2. Validation Testing**
- **Create unit tests** for each model with missing field scenarios
- **Test pipeline methods** that create models from dictionaries
- **Include round-trip conversion tests** in test suites

### **3. Development Workflow**
- **Run validation tests** before committing model changes
- **Test with actual pipeline data** not just mock data
- **Validate error messages** provide clear field information

## **Common Validation Errors**

### **Missing Required Fields**
```python
# Error: Field required [type=missing, input_value={...}, input_type=dict]
# Solution: Add all required fields to model creation
```

### **Type Mismatches**
```python
# Error: Input should be a valid integer [type=int_parsing, input_value='string', input_type=str]
# Solution: Ensure correct types for all fields
```

### **Invalid Enum Values**
```python
# Error: Input should be 'value1', 'value2' or 'value3' [type=enum, input_value='invalid']
# Solution: Use valid enum values from model definition
```

## **Testing Requirements**
- **Every Pydantic model** must have validation tests
- **Pipeline methods creating models** must have integration tests
- **Round-trip conversion** must be tested for state-managed models
- **Error scenarios** must be tested with pytest.raises(ValidationError)

## **Model Documentation**
- **Document all required fields** in model docstrings
- **Provide usage examples** showing proper instantiation
- **Include validation error examples** in documentation
- **Cross-reference related models** and transformation utilities

## **Integration with Task Master**
- **Add validation tests** as subtasks when creating new models
- **Include "test model validation"** in implementation details
- **Update existing tests** when modifying model requirements
- **Document validation fixes** in task completion notes

## **Critical: Import Structure & Project Setup**

### ✅ DO: Always Run Streamlit from Project Root
```bash
# CORRECT: Run from project root using launcher
streamlit run streamlit_app_opportunity.py

# INCORRECT: Running directly from src/frontend/ causes import errors
streamlit run src/frontend/streamlit_app_opportunity.py  # DON'T DO THIS
```

### ✅ DO: Use Proper Import Patterns
```python
# For files that may be run directly, use try/except pattern:
try:
    # Try relative imports first (when run through launcher)
    from ..backend.pipelines.main_langgraph_opportunity import opportunity_graph
    from .components.progressive_disclosure import render_opportunities
except ImportError:
    # Fall back to absolute imports (when run directly)
    from src.backend.pipelines.main_langgraph_opportunity import opportunity_graph
    from src.frontend.components.progressive_disclosure import render_opportunities
```

### ❌ DON'T: Use Only Relative Imports in Entry Points
```python
# This will fail when run directly:
from ..backend.pipelines.main_langgraph_opportunity import opportunity_graph  # BAD
```

## **Critical: CategoryOpportunity Validation Requirements**

### ✅ DO: Always Include Required Fields for CategoryOpportunity
```python
# CategoryOpportunity REQUIRES these fields:
category_opp = CategoryOpportunity(
    id=1,                           # REQUIRED: int or str
    opportunity="Opportunity name", # REQUIRED: str
    category_type="brand",          # REQUIRED: str (brand/product/pricing/market)
    current_gap="Gap description",  # REQUIRED: str
    recommendation="Recommendation", # REQUIRED: str
    implementation="Implementation", # REQUIRED: str
    timeline="6-12 months",         # REQUIRED: str
    investment="Medium investment"  # REQUIRED: str
)
```

### ❌ DON'T: Create CategoryOpportunity Without Required Fields
```python
# This will cause ValidationError:
category_opp = CategoryOpportunity(
    opportunity="Test Opportunity"
    # Missing: id, category_type, current_gap, etc.
)
```

## **Safe Model Creation Patterns**

### ✅ DO: Use Helper Methods for Safe Model Creation
```python
def _safe_recreate_category_opportunities(self, opportunities_data: List[Dict], category_type: str) -> List[CategoryOpportunity]:
    """Safely recreate CategoryOpportunity objects with required fields"""
    safe_opportunities = []
    
    for i, opp_data in enumerate(opportunities_data):
        try:
            safe_opp = CategoryOpportunity(
                id=opp_data.get("id", i + 1),
                opportunity=opp_data.get("opportunity", f"Opportunity {i + 1}"),
                category_type=opp_data.get("category_type", category_type),
                current_gap=opp_data.get("current_gap", f"Gap in {category_type}"),
                recommendation=opp_data.get("recommendation", "Recommendation needed"),
                implementation=opp_data.get("implementation", "Implementation plan needed"),
                timeline=opp_data.get("timeline", "6-12 months"),
                investment=opp_data.get("investment", "Medium investment")
            )
            safe_opportunities.append(safe_opp)
        except Exception as e:
            print(f"Warning: Failed to create CategoryOpportunity {i}: {e}")
            continue
    
    return safe_opportunities
```

### ✅ DO: Validate Data Before Model Creation
```python
def validate_category_opportunity_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and enhance data before CategoryOpportunity creation"""
    required_fields = {
        "id": data.get("id", 1),
        "opportunity": data.get("opportunity", "Strategic Opportunity"),
        "category_type": data.get("category_type", "brand"),
        "current_gap": data.get("current_gap", "Competitive gap identified"),
        "recommendation": data.get("recommendation", "Strategic recommendation"),
        "implementation": data.get("implementation", "Implementation plan"),
        "timeline": data.get("timeline", "6-12 months"),
        "investment": data.get("investment", "Medium investment")
    }
    return required_fields
```

## **Common Error Patterns & Fixes**

### ❌ Error: "Field required [type=missing, input_value={...}]"
**Cause**: Missing required fields in CategoryOpportunity creation
**Fix**: Use safe creation patterns above or validate data first

### ❌ Error: "ImportError: attempted relative import with no known parent package"
**Cause**: Running Streamlit app directly from src/frontend/ directory
**Fix**: Always run from project root: `streamlit run streamlit_app_opportunity.py`

### ❌ Error: "set_page_config() can only be called once per app page"
**Cause**: Multiple st.set_page_config() calls or imports with Streamlit commands
**Fix**: Ensure st.set_page_config() is the first Streamlit command after import streamlit

## **Graceful Error Handling**

### ✅ DO: Handle Missing Fields Gracefully
```python
try:
    opportunities = [CategoryOpportunity(**opp_data) for opp_data in raw_data]
except ValidationError as e:
    # Log the error and use safe creation
    print(f"Validation error: {e}")
    opportunities = self._safe_recreate_category_opportunities(raw_data, "brand")
```

### ✅ DO: Provide Meaningful Defaults
```python
# Always provide sensible defaults for required fields
default_values = {
    "id": lambda i: i + 1,
    "category_type": "brand",
    "current_gap": "Competitive analysis required",
    "recommendation": "Strategic recommendation needed",
    "implementation": "Implementation plan required",
    "timeline": "6-12 months",
    "investment": "Medium investment required"
}
```

## **Testing Requirements**

### ✅ DO: Test All Model Creation Paths
```python
def test_category_opportunity_with_all_required_fields(self):
    """Test CategoryOpportunity creation with all required fields"""
    data = {
        "id": 1,
        "opportunity": "Test Opportunity",
        "category_type": "brand",
        "current_gap": "Test gap",
        "recommendation": "Test recommendation",
        "implementation": "Test implementation",
        "timeline": "6-12 months",
        "investment": "Medium investment"
    }
    
    opp = CategoryOpportunity(**data)
    assert opp.id == 1
    assert opp.category_type == "brand"
```

### ✅ DO: Test Error Conditions
```python
def test_category_opportunity_missing_required_fields_raises_error(self):
    """Test that missing required fields raise ValidationError"""
    incomplete_data = {"opportunity": "Test Opportunity"}
    
    with pytest.raises(ValidationError) as exc_info:
        CategoryOpportunity(**incomplete_data)
    
    assert "Field required" in str(exc_info.value)
```

## **Project Structure Validation**

### ✅ DO: Maintain Proper File Structure
```
ortho-intel/
├── streamlit_app_opportunity.py          # 🎯 MAIN LAUNCHER - Use this!
├── src/
│   ├── frontend/
│   │   ├── streamlit_app_opportunity.py  # Actual frontend code
│   │   └── components/
│   └── backend/
│       ├── pipelines/
│       └── core/
└── README.md
```

### ✅ DO: Use Launcher Pattern for Entry Points
```python
#!/usr/bin/env python3
"""
Main entry point for Orthopedic Intelligence Platform
Imports from restructured frontend components
"""

# Import and run the main frontend application
from src.frontend.streamlit_app_opportunity import main

if __name__ == "__main__":
    main()
```

---

**Remember**: Always test model creation and imports before making pipeline changes!
