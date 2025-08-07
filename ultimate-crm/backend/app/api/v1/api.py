"""
Main API router for Ultimate CRM System
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, customers, leads, opportunities,
    contacts, activities, campaigns, tickets, products, invoices
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Core CRM endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])