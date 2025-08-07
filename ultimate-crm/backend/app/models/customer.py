"""
Customer models for comprehensive customer relationship management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from enum import Enum

from app.core.database import Base


class CustomerType(str, Enum):
    """Customer type enumeration"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class CustomerStatus(str, Enum):
    """Customer status enumeration"""
    PROSPECT = "prospect"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    BLACKLISTED = "blacklisted"


class Customer(Base):
    """Comprehensive customer model for 360-degree customer view"""
    
    __tablename__ = "customers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    customer_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(SQLEnum(CustomerType), nullable=False, default=CustomerType.INDIVIDUAL)
    status = Column(SQLEnum(CustomerStatus), nullable=False, default=CustomerStatus.PROSPECT)
    
    # Contact information
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business information (for business customers)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    annual_revenue = Column(Numeric(15, 2), nullable=True)
    tax_id = Column(String(50), nullable=True)
    
    # Individual information (for individual customers)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Customer value metrics
    lifetime_value = Column(Numeric(15, 2), nullable=True, default=0)
    total_revenue = Column(Numeric(15, 2), nullable=True, default=0)
    total_orders = Column(Integer, nullable=False, default=0)
    average_order_value = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Engagement metrics
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    last_purchase_date = Column(DateTime(timezone=True), nullable=True)
    engagement_score = Column(Integer, nullable=True, default=0)
    satisfaction_score = Column(Numeric(3, 2), nullable=True)  # 0-10 scale
    
    # Risk assessment
    churn_risk_score = Column(Numeric(3, 2), nullable=True)  # 0-1 scale
    credit_score = Column(Integer, nullable=True)
    payment_terms = Column(String(50), nullable=True)
    
    # Preferences and segmentation
    preferred_contact_method = Column(String(50), nullable=True)
    preferred_language = Column(String(10), nullable=True, default="en")
    timezone = Column(String(50), nullable=True, default="UTC")
    marketing_opt_in = Column(Boolean, default=True, nullable=False)
    
    # Custom fields
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Source and attribution
    source = Column(String(100), nullable=True)
    referrer = Column(String(255), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    first_contact_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    segment_id = Column(UUID(as_uuid=True), ForeignKey('customer_segments.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_customers")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    segment = relationship("CustomerSegment", back_populates="customers")
    notes = relationship("CustomerNote", back_populates="customer", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="customer")
    opportunities = relationship("Opportunity", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")
    activities = relationship("Activity", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(number='{self.customer_number}', name='{self.name}')>"
    
    @property
    def full_name(self):
        """Get customer's full name (for individuals)"""
        if self.type == CustomerType.INDIVIDUAL and self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name
    
    @property
    def display_name(self):
        """Get display name for customer"""
        return self.full_name or self.name
    
    def calculate_health_score(self):
        """Calculate customer health score based on various metrics"""
        score = 0
        
        # Engagement score (0-40 points)
        if self.engagement_score:
            score += min(self.engagement_score * 0.4, 40)
        
        # Satisfaction score (0-20 points)
        if self.satisfaction_score:
            score += self.satisfaction_score * 2
        
        # Recent activity (0-20 points)
        if self.last_contact_date:
            days_since_contact = (datetime.utcnow() - self.last_contact_date).days
            if days_since_contact <= 30:
                score += 20
            elif days_since_contact <= 90:
                score += 10
        
        # Revenue contribution (0-20 points)
        if self.total_revenue and self.total_revenue > 0:
            score += min(float(self.total_revenue) / 1000, 20)
        
        return min(score, 100)
    
    def add_tag(self, tag: str):
        """Add tag to customer"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from customer"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list


class CustomerSegment(Base):
    """Customer segmentation model"""
    
    __tablename__ = "customer_segments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Segment information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Segment criteria
    criteria = Column(JSONB, nullable=False, default={})
    
    # Segment metrics
    customer_count = Column(Integer, nullable=False, default=0)
    average_value = Column(Numeric(15, 2), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_dynamic = Column(Boolean, default=False, nullable=False)  # Auto-update based on criteria
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_calculated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    customers = relationship("Customer", back_populates="segment")
    
    def __repr__(self):
        return f"<CustomerSegment(name='{self.name}', count={self.customer_count})>"


class CustomerNote(Base):
    """Customer notes and interactions"""
    
    __tablename__ = "customer_notes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Note content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=True)  # call, meeting, email, etc.
    
    # Visibility and importance
    is_private = Column(Boolean, default=False, nullable=False)
    is_important = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="notes")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<CustomerNote(customer_id='{self.customer_id}', title='{self.title}')>"