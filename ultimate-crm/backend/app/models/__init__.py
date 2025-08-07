"""
Database models for Ultimate CRM System
"""

# Import all models to ensure they are registered with SQLAlchemy
from .user import User, Role, UserRole
from .customer import Customer, CustomerSegment, CustomerNote
from .lead import Lead, LeadSource, LeadScore
from .opportunity import Opportunity, OpportunityStage, OpportunityProduct
from .contact import Contact, ContactMethod
from .activity import Activity, ActivityType, Task
from .campaign import Campaign, CampaignTarget, CampaignMetric
from .ticket import Ticket, TicketCategory, TicketComment
from .product import Product, ProductCategory, PricingTier
from .invoice import Invoice, InvoiceItem, Payment

__all__ = [
    # User management
    "User", "Role", "UserRole",
    
    # Customer management
    "Customer", "CustomerSegment", "CustomerNote",
    
    # Lead management
    "Lead", "LeadSource", "LeadScore",
    
    # Opportunity management
    "Opportunity", "OpportunityStage", "OpportunityProduct",
    
    # Contact management
    "Contact", "ContactMethod",
    
    # Activity management
    "Activity", "ActivityType", "Task",
    
    # Campaign management
    "Campaign", "CampaignTarget", "CampaignMetric",
    
    # Support management
    "Ticket", "TicketCategory", "TicketComment",
    
    # Product management
    "Product", "ProductCategory", "PricingTier",
    
    # Financial management
    "Invoice", "InvoiceItem", "Payment",
]