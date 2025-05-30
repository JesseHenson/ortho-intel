# demo_data.py
"""
Demo data for opportunity-first competitive intelligence frontend
Focused on actionable insights for medical device manufacturing companies
"""

from typing import Dict, List, Any
from datetime import datetime

# Demo competitive analysis result with opportunity-first structure
DEMO_ANALYSIS_RESULT = {
    "analysis_metadata": {
        "client_company": "MedTech Innovations Inc.",
        "analysis_date": "2024-01-15",
        "competitors_analyzed": ["Stryker Spine", "Zimmer Biomet", "Medtronic Spine"],
        "device_category": "Spine Fusion",
        "analysis_type": "Competitive Opportunity Intelligence"
    },
    
    # TOP OPPORTUNITIES - Hero section data
    "top_opportunities": [
        {
            "id": 1,
            "title": "AI-Powered Surgical Planning Gap",
            "category": "Product Innovation",
            "description": "None of the top 3 competitors offer AI-powered pre-surgical planning tools. Massive opportunity for differentiation.",
            "opportunity_score": 9.2,
            "implementation_difficulty": "Medium",
            "time_to_market": "12-18 months",
            "investment_level": "High",
            "competitive_risk": "Medium",
            "potential_impact": "$50M+ revenue opportunity",
            "next_steps": [
                "Partner with AI/ML company",
                "Develop MVP surgical planning software",
                "Pilot with 3-5 key surgeon customers"
            ],
            "supporting_evidence": "Market research shows 78% of spine surgeons want better planning tools"
        },
        {
            "id": 2,
            "title": "Value-Based Care Positioning",
            "category": "Brand Strategy",
            "description": "Competitors focus on device features. Opportunity to lead with patient outcomes and cost-effectiveness messaging.",
            "opportunity_score": 8.7,
            "implementation_difficulty": "Easy",
            "time_to_market": "3-6 months",
            "investment_level": "Low",
            "competitive_risk": "Low",
            "potential_impact": "15-20% premium pricing",
            "next_steps": [
                "Develop outcome-focused marketing materials",
                "Create ROI calculator for hospitals",
                "Train sales team on value-based selling"
            ],
            "supporting_evidence": "Hospital buyers increasingly focused on total cost of care"
        },
        {
            "id": 3,
            "title": "Minimally Invasive Premium Segment",
            "category": "Market Positioning",
            "description": "Stryker dominates traditional, but minimally invasive premium segment ($15K+ devices) is underserved.",
            "opportunity_score": 8.1,
            "implementation_difficulty": "Medium",
            "time_to_market": "6-12 months",
            "investment_level": "Medium",
            "competitive_risk": "Medium",
            "potential_impact": "$30M market segment",
            "next_steps": [
                "Develop premium minimally invasive product line",
                "Target high-volume spine centers",
                "Create surgeon training program"
            ],
            "supporting_evidence": "Market growing 12% annually, limited premium options"
        }
    ],
    
    # OPPORTUNITY MATRIX DATA
    "opportunity_matrix": {
        "high_impact_easy": [
            {"name": "Value-Based Messaging", "impact": 8.7, "difficulty": 2.1},
            {"name": "Surgeon Education Program", "impact": 7.8, "difficulty": 2.8}
        ],
        "high_impact_hard": [
            {"name": "AI Surgical Planning", "impact": 9.2, "difficulty": 7.5},
            {"name": "Robotic Integration", "impact": 8.9, "difficulty": 8.2}
        ],
        "low_impact_easy": [
            {"name": "Website Redesign", "impact": 4.2, "difficulty": 1.5},
            {"name": "Social Media Strategy", "impact": 3.8, "difficulty": 2.0}
        ],
        "low_impact_hard": [
            {"name": "New Manufacturing Facility", "impact": 5.1, "difficulty": 9.0}
        ]
    },
    
    # CATEGORY-SPECIFIC OPPORTUNITIES
    "brand_opportunities": [
        {
            "opportunity": "Outcome-Focused Positioning",
            "current_gap": "Competitors focus on device specs, not patient outcomes",
            "recommendation": "Lead with '30% faster recovery' messaging",
            "implementation": "Rebrand around patient outcomes, create outcome studies",
            "timeline": "3-6 months",
            "investment": "Low ($50K-100K)"
        },
        {
            "opportunity": "Surgeon-Centric Brand",
            "current_gap": "Generic medical device branding across competitors",
            "recommendation": "Build brand specifically for spine surgeons",
            "implementation": "Surgeon advisory board, surgeon-designed marketing",
            "timeline": "6-12 months", 
            "investment": "Medium ($200K-500K)"
        }
    ],
    
    "product_opportunities": [
        {
            "opportunity": "AI-Powered Planning Software",
            "current_gap": "No competitor offers integrated AI planning",
            "recommendation": "Develop AI surgical planning companion app",
            "implementation": "Partner with AI company, develop MVP, pilot test",
            "timeline": "12-18 months",
            "investment": "High ($1M-2M)"
        },
        {
            "opportunity": "Biodegradable Implant Materials",
            "current_gap": "All competitors use permanent titanium",
            "recommendation": "Develop biodegradable spine fusion materials",
            "implementation": "R&D partnership, clinical trials, FDA approval",
            "timeline": "24-36 months",
            "investment": "High ($2M-5M)"
        }
    ],
    
    "pricing_opportunities": [
        {
            "opportunity": "Premium Minimally Invasive Tier",
            "current_gap": "No premium options above $12K price point",
            "recommendation": "Launch $15K-20K premium product line",
            "implementation": "Develop premium features, target high-volume centers",
            "timeline": "6-12 months",
            "investment": "Medium ($500K-1M)"
        },
        {
            "opportunity": "Value-Based Pricing Model",
            "current_gap": "All competitors use traditional device pricing",
            "recommendation": "Outcome-based pricing with risk sharing",
            "implementation": "Pilot with 2-3 health systems, track outcomes",
            "timeline": "12-18 months",
            "investment": "Low ($100K-300K)"
        }
    ],
    
    "market_opportunities": [
        {
            "opportunity": "Ambulatory Surgery Centers",
            "current_gap": "Competitors focus on hospitals, ASCs underserved",
            "recommendation": "Develop ASC-specific product line and support",
            "implementation": "ASC-focused sales team, specialized products",
            "timeline": "6-12 months",
            "investment": "Medium ($300K-800K)"
        },
        {
            "opportunity": "International Expansion - Southeast Asia",
            "current_gap": "Limited competitor presence in growing markets",
            "recommendation": "Enter Thailand, Vietnam, Philippines markets",
            "implementation": "Local partnerships, regulatory approval, distribution",
            "timeline": "18-24 months",
            "investment": "High ($1M-3M)"
        }
    ],
    
    # COMPETITIVE LANDSCAPE (supporting information)
    "competitive_landscape": {
        "market_leaders": {
            "Stryker Spine": {
                "market_share": "28%",
                "strengths": ["Brand recognition", "Sales force", "R&D budget"],
                "weaknesses": ["High prices", "Limited innovation", "Complex products"],
                "opportunities_against": ["Price-sensitive segments", "Innovation gaps", "Simplicity"]
            },
            "Zimmer Biomet": {
                "market_share": "22%", 
                "strengths": ["Product portfolio", "Global reach", "Manufacturing"],
                "weaknesses": ["Brand perception", "Surgeon relationships", "Digital lag"],
                "opportunities_against": ["Digital innovation", "Surgeon engagement", "Premium positioning"]
            },
            "Medtronic Spine": {
                "market_share": "18%",
                "strengths": ["Technology", "Clinical data", "Global presence"],
                "weaknesses": ["Complex portfolio", "High costs", "Slow innovation"],
                "opportunities_against": ["Simplified solutions", "Cost-effective options", "Faster innovation"]
            }
        }
    },
    
    # EXECUTIVE SUMMARY
    "executive_summary": {
        "key_insight": "Massive opportunity in AI-powered surgical planning and value-based positioning while competitors focus on traditional device features.",
        "total_opportunities": 12,
        "high_priority_opportunities": 3,
        "estimated_revenue_impact": "$95M+ over 3 years",
        "recommended_immediate_actions": [
            "Launch value-based marketing campaign (3 months, $75K)",
            "Begin AI surgical planning partnership discussions (immediate)",
            "Develop premium minimally invasive product roadmap (6 months)"
        ]
    }
}

# Additional demo data for different scenarios
DEMO_SCENARIOS = {
    "cardiovascular": {
        "client_company": "CardioTech Solutions",
        "top_opportunity": "Remote Patient Monitoring Integration",
        "key_gap": "Competitors lack integrated RPM capabilities"
    },
    "joint_replacement": {
        "client_company": "JointCare Innovations", 
        "top_opportunity": "Personalized 3D-Printed Implants",
        "key_gap": "One-size-fits-all approach by major players"
    },
    "diabetes_care": {
        "client_company": "GlucoSmart Technologies",
        "top_opportunity": "AI-Powered Glucose Prediction",
        "key_gap": "Reactive vs. predictive glucose management"
    }
}

def get_demo_data(category: str = "spine_fusion") -> Dict[str, Any]:
    """Get demo data for specified category"""
    if category == "spine_fusion":
        return DEMO_ANALYSIS_RESULT
    else:
        # Return modified version for other categories
        base_data = DEMO_ANALYSIS_RESULT.copy()
        if category in DEMO_SCENARIOS:
            scenario = DEMO_SCENARIOS[category]
            base_data["analysis_metadata"]["client_company"] = scenario["client_company"]
            base_data["top_opportunities"][0]["title"] = scenario["top_opportunity"]
            base_data["top_opportunities"][0]["description"] = f"{scenario['key_gap']}. Major opportunity for differentiation."
        return base_data 