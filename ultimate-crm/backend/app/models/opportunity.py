"""
Opportunity models for sales pipeline management and forecasting
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class OpportunityStatus(str, Enum):
    """Opportunity status enumeration"""
    OPEN = "open"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


class OpportunityPriority(str, Enum):
    """Opportunity priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Association table for opportunity products
opportunity_products = Table(
    'opportunity_products',
    Base.metadata,
    Column('opportunity_id', UUID(as_uuid=True), ForeignKey('opportunities.id'), primary_key=True),
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True),
    Column('quantity', Integer, nullable=False, default=1),
    Column('unit_price', Numeric(15, 2), nullable=False),
    Column('discount_percent', Numeric(5, 2), nullable=True, default=0),
    Column('total_amount', Numeric(15, 2), nullable=False)
)


class Opportunity(Base):
    """Sales opportunity model for pipeline management"""
    
    __tablename__ = "opportunities"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    opportunity_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(SQLEnum(OpportunityStatus), nullable=False, default=OpportunityStatus.OPEN)
    priority = Column(SQLEnum(OpportunityPriority), nullable=False, default=OpportunityPriority.MEDIUM)
    
    # Financial information
    amount = Column(Numeric(15, 2), nullable=False)
    expected_revenue = Column(Numeric(15, 2), nullable=True)
    probability = Column(Integer, nullable=False, default=0)  # 0-100%
    weighted_amount = Column(Numeric(15, 2), nullable=True)  # amount * probability
    
    # Timeline
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    actual_close_date = Column(DateTime(timezone=True), nullable=True)
    sales_cycle_days = Column(Integer, nullable=True)
    
    # Pipeline stage
    stage_id = Column(UUID(as_uuid=True), ForeignKey('opportunity_stages.id'), nullable=False)
    stage_changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Competition and risks
    competitors = Column(JSONB, nullable=True, default=[])
    risks = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    
    # Source and attribution
    source = Column(String(100), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'), nullable=True)
    
    # Custom fields and tags
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="opportunities")
    lead = relationship("Lead")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_opportunities")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    stage = relationship("OpportunityStage", back_populates="opportunities")
    campaign = relationship("Campaign")
    products = relationship("Product", secondary=opportunity_products)
    product_details = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="opportunity")
    
    def __repr__(self):
        return f"<Opportunity(number='{self.opportunity_number}', name='{self.name}')>"
    
    def calculate_weighted_amount(self):
        """Calculate weighted amount based on probability"""
        if self.amount and self.probability:
            self.weighted_amount = self.amount * (self.probability / 100)
        else:
            self.weighted_amount = 0
        return self.weighted_amount
    
    def calculate_sales_cycle(self):
        """Calculate sales cycle duration"""
        if self.actual_close_date and self.created_at:
            self.sales_cycle_days = (self.actual_close_date - self.created_at).days
        return self.sales_cycle_days
    
    def advance_stage(self, new_stage_id: str):
        """Advance opportunity to next stage"""
        self.stage_id = new_stage_id
        self.stage_changed_at = func.now()
    
    def add_competitor(self, competitor: str):
        """Add competitor to opportunity"""
        if competitor not in self.competitors:
            self.competitors = self.competitors + [competitor]
    
    def remove_competitor(self, competitor: str):
        """Remove competitor from opportunity"""
        if competitor in self.competitors:
            competitors_list = list(self.competitors)
            competitors_list.remove(competitor)
            self.competitors = competitors_list
    
    def add_tag(self, tag: str):
        """Add tag to opportunity"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from opportunity"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list


class OpportunityStage(Base):
    """Sales pipeline stages"""
    
    __tablename__ = "opportunity_stages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Stage information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    
    # Stage configuration
    probability_default = Column(Integer, nullable=False, default=0)  # Default probability for this stage
    is_closed_won = Column(Boolean, default=False, nullable=False)
    is_closed_lost = Column(Boolean, default=False, nullable=False)
    
    # Stage metrics
    average_duration_days = Column(Integer, nullable=True)
    conversion_rate = Column(Numeric(5, 2), nullable=True)
    
    # Visual configuration
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    opportunities = relationship("Opportunity", back_populates="stage")
    
    def __repr__(self):
        return f"<OpportunityStage(name='{self.name}', order={self.order_index})>"


class OpportunityProduct(Base):
    """Products associated with opportunities"""
    
    __tablename__ = "opportunity_product_details"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product information
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), nullable=True, default=0)
    discount_amount = Column(Numeric(15, 2), nullable=True, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Additional information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunities.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="product_details")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OpportunityProduct(opportunity_id='{self.opportunity_id}', product_id='{self.product_id}')>"
    
    def calculate_total(self):
        """Calculate total amount including discounts"""
        subtotal = self.quantity * self.unit_price
        
        if self.discount_percent:
            self.discount_amount = subtotal * (self.discount_percent / 100)
        
        self.total_amount = subtotal - (self.discount_amount or 0)
        return self.total_amount


# Default opportunity stages
DEFAULT_OPPORTUNITY_STAGES = [
    {
        "name": "Prospecting",
        "description": "Initial contact and qualification",
        "order_index": 1,
        "probability_default": 10,
        "color": "#FF6B6B"
    },
    {
        "name": "Qualification",
        "description": "Needs assessment and budget confirmation",
        "order_index": 2,
        "probability_default": 25,
        "color": "#4ECDC4"
    },
    {
        "name": "Proposal",
        "description": "Solution presentation and proposal",
        "order_index": 3,
        "probability_default": 50,
        "color": "#45B7D1"
    },
    {
        "name": "Negotiation",
        "description": "Contract negotiation and terms discussion",
        "order_index": 4,
        "probability_default": 75,
        "color": "#FFA726"
    },
    {
        "name": "Closed Won",
        "description": "Deal successfully closed",
        "order_index": 5,
        "probability_default": 100,
        "is_closed_won": True,
        "color": "#66BB6A"
    },
    {
        "name": "Closed Lost",
        "description": "Deal lost to competitor or abandoned",
        "order_index": 6,
        "probability_default": 0,
        "is_closed_lost": True,
        "color": "#EF5350"
    }
]