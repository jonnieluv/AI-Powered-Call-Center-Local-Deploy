"""
Ultimate CRM System - Simplified Main Application
Runs without database dependencies for demo purposes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
from datetime import datetime
import uuid

# Create FastAPI application
app = FastAPI(
    title="Ultimate CRM System",
    description="Comprehensive CRM system built on VAST architecture with AI-driven automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class CustomerResponse(BaseModel):
    id: str
    customer_number: str
    name: str
    email: str
    status: str
    created_at: datetime
    health_score: int

class LeadResponse(BaseModel):
    id: str
    lead_number: str
    first_name: str
    last_name: str
    email: str
    company: str
    status: str
    lead_score: int
    quality: str
    created_at: datetime

class OpportunityResponse(BaseModel):
    id: str
    opportunity_number: str
    name: str
    amount: float
    probability: int
    status: str
    stage: str
    expected_close_date: datetime
    created_at: datetime

class SystemStats(BaseModel):
    total_customers: int
    total_leads: int
    total_opportunities: int
    total_revenue: float
    conversion_rate: float
    avg_deal_size: float

# Mock data
mock_customers = [
    {
        "id": str(uuid.uuid4()),
        "customer_number": "CUST-000001",
        "name": "Acme Corporation",
        "email": "contact@acme.com",
        "status": "active",
        "created_at": datetime.now(),
        "health_score": 85
    },
    {
        "id": str(uuid.uuid4()),
        "customer_number": "CUST-000002",
        "name": "TechStart Inc",
        "email": "hello@techstart.com",
        "status": "active",
        "created_at": datetime.now(),
        "health_score": 92
    },
    {
        "id": str(uuid.uuid4()),
        "customer_number": "CUST-000003",
        "name": "Global Solutions Ltd",
        "email": "info@globalsolutions.com",
        "status": "prospect",
        "created_at": datetime.now(),
        "health_score": 67
    }
]

mock_leads = [
    {
        "id": str(uuid.uuid4()),
        "lead_number": "LEAD-000001",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com",
        "company": "Innovation Labs",
        "status": "qualified",
        "lead_score": 87,
        "quality": "hot",
        "created_at": datetime.now()
    },
    {
        "id": str(uuid.uuid4()),
        "lead_number": "LEAD-000002",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson@company.com",
        "company": "Enterprise Corp",
        "status": "new",
        "lead_score": 65,
        "quality": "warm",
        "created_at": datetime.now()
    },
    {
        "id": str(uuid.uuid4()),
        "lead_number": "LEAD-000003",
        "first_name": "Mike",
        "last_name": "Davis",
        "email": "mike.davis@startup.io",
        "company": "Future Tech",
        "status": "contacted",
        "lead_score": 45,
        "quality": "cold",
        "created_at": datetime.now()
    }
]

mock_opportunities = [
    {
        "id": str(uuid.uuid4()),
        "opportunity_number": "OPP-000001",
        "name": "Enterprise Software License",
        "amount": 150000.0,
        "probability": 75,
        "status": "open",
        "stage": "Negotiation",
        "expected_close_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "id": str(uuid.uuid4()),
        "opportunity_number": "OPP-000002",
        "name": "Professional Services Contract",
        "amount": 85000.0,
        "probability": 50,
        "status": "open",
        "stage": "Proposal",
        "expected_close_date": datetime.now(),
        "created_at": datetime.now()
    }
]

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ultimate CRM System API",
        "version": "1.0.0",
        "architecture": "VAST (Vertical AI System Topology)",
        "status": "operational",
        "features": [
            "360-degree customer view",
            "AI-powered lead scoring",
            "Predictive analytics",
            "Sales pipeline management",
            "Marketing automation",
            "Customer service ticketing"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": "operational",
            "ai_agents": "operational",
            "analytics": "operational"
        }
    }

@app.get("/api/v1/customers", response_model=List[CustomerResponse])
async def list_customers():
    """List all customers"""
    return mock_customers

@app.get("/api/v1/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """Get customer by ID"""
    customer = next((c for c in mock_customers if c["id"] == customer_id), None)
    if not customer:
        return {"error": "Customer not found"}, 404
    return customer

@app.get("/api/v1/leads", response_model=List[LeadResponse])
async def list_leads():
    """List all leads"""
    return mock_leads

@app.get("/api/v1/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    """Get lead by ID"""
    lead = next((l for l in mock_leads if l["id"] == lead_id), None)
    if not lead:
        return {"error": "Lead not found"}, 404
    return lead

@app.get("/api/v1/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities():
    """List all opportunities"""
    return mock_opportunities

@app.get("/api/v1/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: str):
    """Get opportunity by ID"""
    opportunity = next((o for o in mock_opportunities if o["id"] == opportunity_id), None)
    if not opportunity:
        return {"error": "Opportunity not found"}, 404
    return opportunity

@app.get("/api/v1/dashboard/stats", response_model=SystemStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_revenue = sum(o["amount"] for o in mock_opportunities)
    return {
        "total_customers": len(mock_customers),
        "total_leads": len(mock_leads),
        "total_opportunities": len(mock_opportunities),
        "total_revenue": total_revenue,
        "conversion_rate": 35.5,
        "avg_deal_size": total_revenue / len(mock_opportunities) if mock_opportunities else 0
    }

@app.get("/api/v1/ai/lead-scoring/{lead_id}")
async def get_lead_ai_analysis(lead_id: str):
    """Get AI-powered lead analysis"""
    lead = next((l for l in mock_leads if l["id"] == lead_id), None)
    if not lead:
        return {"error": "Lead not found"}, 404
    
    return {
        "lead_id": lead_id,
        "lead_score": lead["lead_score"],
        "quality": lead["quality"],
        "analysis": {
            "demographic_score": 28,
            "behavioral_score": 35,
            "engagement_score": 24,
            "confidence": 0.87,
            "recommendations": [
                "Schedule a product demo within 48 hours",
                "Send personalized case study relevant to their industry",
                "Connect with decision maker via LinkedIn"
            ],
            "risk_factors": [
                "No recent website activity",
                "Email engagement declining"
            ],
            "next_best_actions": [
                "Phone call follow-up",
                "Industry-specific content share",
                "Executive briefing invitation"
            ]
        }
    }

@app.get("/api/v1/ai/customer-health/{customer_id}")
async def get_customer_health_analysis(customer_id: str):
    """Get AI-powered customer health analysis"""
    customer = next((c for c in mock_customers if c["id"] == customer_id), None)
    if not customer:
        return {"error": "Customer not found"}, 404
    
    return {
        "customer_id": customer_id,
        "health_score": customer["health_score"],
        "status": customer["status"],
        "analysis": {
            "churn_risk": 0.15,
            "lifetime_value": 245000,
            "engagement_trend": "increasing",
            "satisfaction_score": 4.2,
            "risk_indicators": [
                "Support ticket volume increased 15%",
                "Usage metrics down 8% this month"
            ],
            "opportunities": [
                "Upsell premium features",
                "Expand to additional departments",
                "Renewal negotiation upcoming"
            ],
            "recommended_actions": [
                "Schedule quarterly business review",
                "Introduce new feature training",
                "Connect with customer success manager"
            ]
        }
    }

@app.get("/api/v1/analytics/sales-forecast")
async def get_sales_forecast():
    """Get AI-powered sales forecast"""
    return {
        "forecast_period": "Q1 2024",
        "predicted_revenue": 875000,
        "confidence_interval": {
            "low": 750000,
            "high": 1000000
        },
        "pipeline_analysis": {
            "total_pipeline_value": 1200000,
            "weighted_pipeline": 650000,
            "deals_likely_to_close": 8,
            "average_deal_size": 108750
        },
        "trends": {
            "month_over_month_growth": 12.5,
            "win_rate_trend": "improving",
            "sales_cycle_trend": "shortening"
        },
        "recommendations": [
            "Focus on high-probability deals in negotiation stage",
            "Accelerate qualification process for new leads",
            "Increase outbound prospecting by 20%"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)