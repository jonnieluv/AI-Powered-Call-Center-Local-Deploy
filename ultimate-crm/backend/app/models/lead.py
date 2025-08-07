"""
Lead management models with AI-powered scoring and qualification
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class LeadStatus(str, Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadQuality(str, Enum):
    """Lead quality enumeration"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class Lead(Base):
    """Lead model with AI-powered scoring and qualification"""
    
    __tablename__ = "leads"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    lead_number = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=False, index=True)
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
    
    # Lead qualification
    status = Column(SQLEnum(LeadStatus), nullable=False, default=LeadStatus.NEW)
    quality = Column(SQLEnum(LeadQuality), nullable=True)
    
    # AI-powered scoring
    lead_score = Column(Integer, nullable=True, default=0)  # 0-100 scale
    demographic_score = Column(Integer, nullable=True, default=0)
    behavioral_score = Column(Integer, nullable=True, default=0)
    engagement_score = Column(Integer, nullable=True, default=0)
    
    # Business information
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    annual_revenue = Column(Numeric(15, 2), nullable=True)
    budget = Column(Numeric(15, 2), nullable=True)
    
    # Interest and needs
    product_interest = Column(JSONB, nullable=True, default=[])
    pain_points = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    decision_timeframe = Column(String(50), nullable=True)
    
    # Engagement tracking
    first_contact_date = Column(DateTime(timezone=True), nullable=True)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    total_interactions = Column(Integer, nullable=False, default=0)
    email_opens = Column(Integer, nullable=False, default=0)
    email_clicks = Column(Integer, nullable=False, default=0)
    website_visits = Column(Integer, nullable=False, default=0)
    
    # Source and attribution
    source_id = Column(UUID(as_uuid=True), ForeignKey('lead_sources.id'), nullable=True)
    referrer = Column(String(255), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_content = Column(String(100), nullable=True)
    utm_term = Column(String(100), nullable=True)
    
    # Custom fields and tags
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    qualified_at = Column(DateTime(timezone=True), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_leads")
    created_by = relationship("User", foreign_keys=[created_by_id])
    customer = relationship("Customer", back_populates="leads")
    source = relationship("LeadSource", back_populates="leads")
    scores = relationship("LeadScore", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead(number='{self.lead_number}', name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Get lead's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def calculate_lead_score(self):
        """Calculate comprehensive lead score using AI algorithms"""
        # Demographic scoring (0-30 points)
        demographic_score = 0
        if self.company_size in ["Large", "Enterprise"]:
            demographic_score += 10
        elif self.company_size in ["Medium"]:
            demographic_score += 5
        
        if self.annual_revenue and self.annual_revenue > 1000000:
            demographic_score += 10
        elif self.annual_revenue and self.annual_revenue > 100000:
            demographic_score += 5
        
        if self.job_title and any(title in self.job_title.lower() for title in ["ceo", "cto", "manager", "director"]):
            demographic_score += 10
        
        # Behavioral scoring (0-40 points)
        behavioral_score = 0
        if self.website_visits > 10:
            behavioral_score += 15
        elif self.website_visits > 5:
            behavioral_score += 10
        elif self.website_visits > 0:
            behavioral_score += 5
        
        if self.email_opens > 5:
            behavioral_score += 10
        elif self.email_opens > 2:
            behavioral_score += 5
        
        if self.email_clicks > 3:
            behavioral_score += 15
        elif self.email_clicks > 0:
            behavioral_score += 10
        
        # Engagement scoring (0-30 points)
        engagement_score = 0
        if self.total_interactions > 10:
            engagement_score += 20
        elif self.total_interactions > 5:
            engagement_score += 15
        elif self.total_interactions > 0:
            engagement_score += 10
        
        if self.last_contact_date:
            from datetime import datetime, timedelta
            days_since_contact = (datetime.utcnow() - self.last_contact_date).days
            if days_since_contact <= 7:
                engagement_score += 10
            elif days_since_contact <= 30:
                engagement_score += 5
        
        # Update individual scores
        self.demographic_score = min(demographic_score, 30)
        self.behavioral_score = min(behavioral_score, 40)
        self.engagement_score = min(engagement_score, 30)
        
        # Calculate total score
        total_score = self.demographic_score + self.behavioral_score + self.engagement_score
        self.lead_score = min(total_score, 100)
        
        # Determine quality based on score
        if self.lead_score >= 80:
            self.quality = LeadQuality.HOT
        elif self.lead_score >= 50:
            self.quality = LeadQuality.WARM
        else:
            self.quality = LeadQuality.COLD
        
        return self.lead_score
    
    def add_tag(self, tag: str):
        """Add tag to lead"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from lead"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list


class LeadSource(Base):
    """Lead source tracking and attribution"""
    
    __tablename__ = "lead_sources"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # organic, paid, social, referral, etc.
    
    # Performance metrics
    total_leads = Column(Integer, nullable=False, default=0)
    qualified_leads = Column(Integer, nullable=False, default=0)
    converted_leads = Column(Integer, nullable=False, default=0)
    conversion_rate = Column(Numeric(5, 2), nullable=True, default=0)
    
    # Cost tracking
    cost_per_lead = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    leads = relationship("Lead", back_populates="source")
    
    def __repr__(self):
        return f"<LeadSource(name='{self.name}', leads={self.total_leads})>"
    
    def update_metrics(self):
        """Update lead source performance metrics"""
        # This would typically be called by a background job
        # to update metrics based on associated leads
        pass


class LeadScore(Base):
    """Historical lead scoring records for AI model training"""
    
    __tablename__ = "lead_scores"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scoring information
    score = Column(Integer, nullable=False)
    demographic_score = Column(Integer, nullable=False, default=0)
    behavioral_score = Column(Integer, nullable=False, default=0)
    engagement_score = Column(Integer, nullable=False, default=0)
    
    # Model information
    model_version = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    confidence = Column(Numeric(3, 2), nullable=True)  # 0-1 scale
    
    # Features used for scoring
    features = Column(JSONB, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Foreign keys
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="scores")
    
    def __repr__(self):
        return f"<LeadScore(lead_id='{self.lead_id}', score={self.score})>"