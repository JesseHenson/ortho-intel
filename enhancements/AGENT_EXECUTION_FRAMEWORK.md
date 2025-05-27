# AGENT EXECUTION FRAMEWORK
## Structured Approach for Phase 2 & 3 Implementation

**Purpose**: Provide clear guidance and guardrails for AI agents implementing advanced features  
**Scope**: Phase 2 (Advanced Intelligence) and Phase 3 (Platform Scaling)  
**Risk Management**: Prevent scope creep and maintain system stability

---

## 🎯 AGENT ONBOARDING CHECKLIST

### Before Starting Any Work
- [ ] Read `CURSOR_CONTEXT.md` for project background
- [ ] Review `PROJECT_HANDOFF.md` for current state
- [ ] Understand `enhancements/PHASE2_ADVANCED_INTELLIGENCE_SPEC.md`
- [ ] Understand `enhancements/PHASE3_PLATFORM_SCALING_SPEC.md`
- [ ] Run validation: `python test_frontend_validation.py`
- [ ] Confirm all tests pass: `python test_cardiovascular_e2e.py`

### Critical Understanding Requirements
```python
# Agent must understand these key concepts:
CORE_ARCHITECTURE = {
    "langgraph_pipeline": "6-node analysis workflow",
    "data_models": "CategoryRouter, SearchTemplates, GraphState",
    "frontend": "Streamlit with 8 demo scenarios",
    "testing": "Comprehensive validation framework"
}

BUSINESS_CONTEXT = {
    "target_users": "Marketing professionals at marketing firms",
    "value_proposition": "AI-powered competitive intelligence",
    "current_status": "Working MVP with 4 device categories",
    "next_phase": "Advanced intelligence capabilities"
}
```

---

## 📋 PHASE-SPECIFIC EXECUTION GUIDES

### Phase 2: Advanced Intelligence Implementation

#### Week 3 Execution Plan
```
Day 1-2: Data Model Extensions
├── Add RegulatoryInsight, PricingInsight, ClinicalEvidence to data_models.py
├── Extend SEARCH_TEMPLATES with new query types
├── Update GraphState schema
└── Test: Ensure no breaking changes

Day 3-4: Regulatory Analysis Node
├── Implement regulatory_analysis_node() in main_langgraph.py
├── Add FDA-specific search and parsing logic
├── Integrate with existing pipeline
└── Test: End-to-end regulatory analysis

Day 5: Pricing Intelligence Node
├── Implement pricing_intelligence_node()
├── Add pricing/reimbursement analysis
└── Test: Pricing insight generation
```

#### Week 4 Execution Plan
```
Day 1-2: Clinical Evidence Node
├── Implement clinical_evidence_node()
├── Add publication search and extraction
└── Test: Clinical evidence mining

Day 3-4: Frontend Integration
├── Update streamlit_app.py for new insights
├── Add analysis depth options (basic/enhanced/comprehensive)
└── Test: User experience with enhanced features

Day 5: Validation & Documentation
├── Comprehensive testing across all categories
├── Performance benchmarking
└── Update handoff documentation
```

#### Phase 2 Quality Gates
```python
# Must pass before proceeding to Phase 3:
PHASE2_REQUIREMENTS = {
    "regulatory_accuracy": ">= 85%",
    "pricing_relevance": ">= 80%", 
    "clinical_evidence": ">= 90%",
    "analysis_time": "< 8 minutes",
    "backward_compatibility": "100%"
}
```

### Phase 3: Platform Scaling Implementation

#### Week 5 Execution Plan
```
Day 1-2: Database Infrastructure
├── Set up PostgreSQL/SQLite schema
├── Implement MarketingFirm, CompetitiveAnalysis models
├── Create migration scripts
└── Test: Database operations and isolation

Day 3: Multi-Tenant Authentication
├── Implement TenantAuth class
├── Add tenant context to operations
├── Update Streamlit for multi-tenant login
└── Test: Authentication and isolation

Day 4-5: Historical Tracking Engine
├── Implement CompetitiveTrendTracker
├── Add analysis result storage
├── Create change detection algorithms
└── Test: Trend detection accuracy
```

#### Week 6 Execution Plan
```
Day 1-2: White-Label Customization
├── Implement WhiteLabelConfig system
├── Update UI for dynamic branding
├── Add custom report generation
└── Test: White-label functionality

Day 3-4: Enterprise Dashboard
├── Create multi-client dashboard
├── Add bulk analysis management
├── Implement usage analytics
└── Test: Dashboard performance

Day 5: Production Deployment
├── Set up production database
├── Configure multi-tenant deployment
├── Performance testing and optimization
└── Test: Full enterprise functionality
```

---

## 🚨 CRITICAL GUARDRAILS

### Absolute Requirements (Never Violate)
1. **Backward Compatibility**: Existing functionality must work unchanged
2. **Performance Limits**: Analysis time must stay within specified bounds
3. **Data Security**: Multi-tenant data must be completely isolated
4. **Test Coverage**: All new features must have comprehensive tests
5. **Rollback Capability**: Every change must be reversible

### Decision Framework
```python
# Use this framework for all implementation decisions:
class DecisionFramework:
    def evaluate_change(self, proposed_change):
        """Evaluate if a change should be implemented"""
        checks = [
            self.breaks_existing_functionality(proposed_change),
            self.exceeds_performance_limits(proposed_change),
            self.lacks_test_coverage(proposed_change),
            self.violates_security_requirements(proposed_change),
            self.outside_specification_scope(proposed_change)
        ]
        return not any(checks)  # Proceed only if all checks pass
```

### When to Stop and Ask for Guidance
- Any existing test fails after your changes
- Performance degrades beyond specified limits
- Implementation requires major architectural changes
- Security concerns arise during development
- Scope creep beyond specification requirements

---

## 🧪 TESTING PROTOCOLS

### Required Testing Sequence
```bash
# Run after every significant change:
1. python test_frontend_validation.py          # Frontend functionality
2. python test_cardiovascular_e2e.py           # Multi-category system
3. python tests/test_backward_compatibility.py # Existing features
4. python tests/test_performance.py            # Performance benchmarks
```

### Phase-Specific Testing
```python
# Phase 2 Testing Requirements:
PHASE2_TESTS = [
    "test_regulatory_analysis.py",
    "test_pricing_intelligence.py", 
    "test_clinical_evidence.py",
    "test_phase2_integration.py",
    "test_phase2_performance.py"
]

# Phase 3 Testing Requirements:
PHASE3_TESTS = [
    "test_multi_tenant_auth.py",
    "test_historical_tracking.py",
    "test_white_label.py",
    "test_enterprise_performance.py",
    "test_data_isolation.py",
    "test_phase3_integration.py"
]
```

### Quality Validation Checklist
- [ ] All existing tests continue to pass
- [ ] New functionality has >90% test coverage
- [ ] Performance benchmarks are met
- [ ] Security requirements are validated
- [ ] User experience is maintained or improved

---

## 📊 PROGRESS TRACKING

### Phase 2 Milestones
```
Week 3:
├── ✅ Data models extended
├── ✅ Regulatory analysis implemented
└── ✅ Pricing intelligence implemented

Week 4:
├── ✅ Clinical evidence implemented
├── ✅ Frontend integration complete
└── ✅ Phase 2 validation passed
```

### Phase 3 Milestones
```
Week 5:
├── ✅ Database infrastructure ready
├── ✅ Multi-tenant authentication working
└── ✅ Historical tracking implemented

Week 6:
├── ✅ White-label customization complete
├── ✅ Enterprise dashboard functional
└── ✅ Production deployment successful
```

### Success Validation
```python
# Phase completion criteria:
PHASE2_SUCCESS = {
    "regulatory_insights": "Generated for 90%+ of analyses",
    "pricing_intelligence": "Actionable for 80%+ of queries",
    "clinical_evidence": "Relevant for 90%+ of competitors",
    "performance": "< 8 minute analysis time maintained"
}

PHASE3_SUCCESS = {
    "multi_tenancy": "3+ firms using platform",
    "data_isolation": "100% separation verified",
    "white_labeling": "Professional reports generated",
    "enterprise_performance": "50+ concurrent analyses supported"
}
```

---

## 🔄 HANDOFF PROCEDURES

### Phase 2 to Phase 3 Handoff
Before starting Phase 3, ensure:
- [ ] All Phase 2 features are working and tested
- [ ] Performance benchmarks are met
- [ ] Documentation is updated
- [ ] Rollback procedures are documented
- [ ] Phase 3 prerequisites are met

### Phase 3 to Production Handoff
Before production deployment:
- [ ] Security penetration testing passed
- [ ] Multi-tenant data isolation verified
- [ ] Performance testing with enterprise load completed
- [ ] Monitoring and alerting configured
- [ ] Support procedures documented

### Documentation Updates Required
After each phase:
- [ ] Update `PROJECT_HANDOFF.md` with new capabilities
- [ ] Update `CURSOR_CONTEXT.md` with current status
- [ ] Create phase-specific completion documentation
- [ ] Update deployment and operational procedures

---

## 📚 AGENT SUCCESS PATTERNS

### Proven Approaches
1. **Incremental Implementation**: Small, testable changes
2. **Test-Driven Development**: Write tests before implementation
3. **Feature Flags**: Enable gradual rollout and easy rollback
4. **Performance Monitoring**: Continuous validation of system performance
5. **Documentation First**: Clear specifications before coding

### Common Pitfalls to Avoid
1. **Scope Creep**: Adding features not in specifications
2. **Breaking Changes**: Modifying existing working functionality
3. **Performance Degradation**: Not monitoring system performance
4. **Security Oversights**: Inadequate multi-tenant isolation
5. **Testing Shortcuts**: Skipping comprehensive validation

### Emergency Procedures
If something goes wrong:
1. **Stop immediately** and assess the situation
2. **Run full test suite** to identify what broke
3. **Revert to last known good state** if necessary
4. **Document the issue** and lessons learned
5. **Ask for guidance** before proceeding

This framework provides the structure and guardrails needed to successfully implement the advanced features while maintaining the stability and quality of the existing platform. 