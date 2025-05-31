---
description: 
globs: 
alwaysApply: false
---
# Task Execution Best Practices

## **Scope Management**

### **Single Responsibility Principle**
- **Each task should have ONE clear objective**
- **Avoid mixing restructuring with feature additions**
- **Separate UI changes from backend refactoring**
- **Keep documentation updates separate from code changes**

### **Task Boundary Respect**
- **Read task description carefully before starting**
- **Stay within defined task scope**
- **Ask for clarification if scope is unclear**
- **Create new tasks for discovered work outside scope**

## **Code Restructuring Tasks**

### **Before Starting**
- **Create backup branch/tag for safety**
- **Document current working state**
- **Take screenshots of UI if frontend is involved**
- **Identify all files that will be affected**

### **During Execution**
- **Move files without modifying content when possible**
- **Update import paths systematically**
- **Test functionality after each major change**
- **Commit logical chunks of work**

### **After Completion**
- **Verify all functionality works identically**
- **Run full test suite**
- **Compare UI appearance if frontend involved**
- **Update documentation to reflect new structure**

## **UI-Related Tasks**

### **Preservation Requirements**
- **Never modify styling during restructuring tasks**
- **Preserve exact visual appearance**
- **Maintain all interactive functionality**
- **Keep responsive behavior intact**

### **Enhancement vs Restructuring**
```python
# ❌ DON'T: Mix restructuring with enhancements
# Task: "Move frontend files to new structure"
# Then also: Add new features, change styling, modify layout

# ✅ DO: Separate concerns
# Task 1: "Move frontend files to new structure" (no UI changes)
# Task 2: "Add client name input field" (UI enhancement)
# Task 3: "Update styling for better UX" (visual changes)
```

## **Testing and Validation**

### **Mandatory Checks**
- **All imports resolve correctly**
- **All tests pass**
- **UI renders identically (if applicable)**
- **Core functionality works as before**
- **No broken dependencies**

### **Documentation Updates**
- **Update README if structure changes**
- **Modify setup instructions if needed**
- **Update import examples in docs**
- **Note any breaking changes**

## **Git Workflow**

### **Commit Practices**
- **Use descriptive commit messages**
- **Separate logical changes into different commits**
- **Include scope in commit message (feat:, fix:, refactor:)**
- **Reference task numbers when applicable**

### **Branch Management**
- **Create feature branches for significant changes**
- **Use descriptive branch names**
- **Keep main branch stable**
- **Test thoroughly before merging**

## **Communication**

### **Progress Updates**
- **Update task status as work progresses**
- **Log implementation notes in subtasks**
- **Document challenges and solutions**
- **Note any scope changes or discoveries**

### **Issue Reporting**
- **Report problems immediately**
- **Provide specific error messages**
- **Include steps to reproduce issues**
- **Suggest potential solutions**

## **Quality Assurance**

### **Code Quality**
- **Maintain existing code style**
- **Follow project conventions**
- **Add comments for complex changes**
- **Remove dead code and unused imports**

### **Performance Considerations**
- **Ensure changes don't degrade performance**
- **Test with realistic data volumes**
- **Monitor memory usage if applicable**
- **Verify startup times remain acceptable**

## **Rollback Preparedness**

### **Safety Measures**
- **Always create backup before major changes**
- **Document rollback procedures**
- **Keep original files accessible during transition**
- **Test rollback process before proceeding**

### **Recovery Planning**
- **Know how to restore previous state**
- **Document any manual steps required**
- **Identify critical files that must be preserved**
- **Plan for partial rollback scenarios**
