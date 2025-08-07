"""
Campaign models for marketing automation and campaign management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class CampaignType(str, Enum):
    """Campaign type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    SOCIAL = "social"
    WEBINAR = "webinar"
    EVENT = "event"
    CONTENT = "content"
    PAID_ADS = "paid_ads"
    DIRECT_MAIL = "direct_mail"


class CampaignStatus(str, Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Association table for campaign targets
campaign_targets = Table(
    'campaign_targets_association',
    Base.metadata,
    Column('campaign_id', UUID(as_uuid=True), ForeignKey('campaigns.id'), primary_key=True),
    Column('target_id', UUID(as_uuid=True), ForeignKey('campaign_targets.id'), primary_key=True)
)


class Campaign(Base):
    """Marketing campaign model"""
    
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    campaign_type = Column(SQLEnum(CampaignType), nullable=False)
    
    # Status and timing
    status = Column(SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Budget and costs
    budget = Column(Numeric(15, 2), nullable=True)
    actual_cost = Column(Numeric(15, 2), nullable=True, default=0)
    cost_per_lead = Column(Numeric(10, 2), nullable=True)
    
    # Content and messaging
    subject_line = Column(String(255), nullable=True)  # For email campaigns
    content = Column(Text, nullable=True)
    call_to_action = Column(String(255), nullable=True)
    landing_page_url = Column(String(500), nullable=True)
    
    # Targeting
    target_audience = Column(Text, nullable=True)
    audience_size = Column(Integer, nullable=True)
    
    # Performance metrics
    sent_count = Column(Integer, nullable=False, default=0)
    delivered_count = Column(Integer, nullable=False, default=0)
    opened_count = Column(Integer, nullable=False, default=0)
    clicked_count = Column(Integer, nullable=False, default=0)
    converted_count = Column(Integer, nullable=False, default=0)
    unsubscribed_count = Column(Integer, nullable=False, default=0)
    
    # Calculated metrics
    delivery_rate = Column(Numeric(5, 2), nullable=True)
    open_rate = Column(Numeric(5, 2), nullable=True)
    click_rate = Column(Numeric(5, 2), nullable=True)
    conversion_rate = Column(Numeric(5, 2), nullable=True)
    roi = Column(Numeric(10, 2), nullable=True)
    
    # Configuration
    is_automated = Column(Boolean, default=False, nullable=False)
    automation_rules = Column(JSONB, nullable=True, default={})
    
    # Custom fields and tags
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    launched_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    segment_id = Column(UUID(as_uuid=True), ForeignKey('customer_segments.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    segment = relationship("CustomerSegment")
    targets = relationship("CampaignTarget", secondary=campaign_targets, back_populates="campaigns")
    metrics = relationship("CampaignMetric", back_populates="campaign", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="campaign")
    
    def __repr__(self):
        return f"<Campaign(name='{self.name}', type='{self.campaign_type}')>"
    
    def calculate_metrics(self):
        """Calculate campaign performance metrics"""
        if self.sent_count > 0:
            self.delivery_rate = (self.delivered_count / self.sent_count) * 100
            
        if self.delivered_count > 0:
            self.open_rate = (self.opened_count / self.delivered_count) * 100
            
        if self.opened_count > 0:
            self.click_rate = (self.clicked_count / self.opened_count) * 100
            
        if self.clicked_count > 0:
            self.conversion_rate = (self.converted_count / self.clicked_count) * 100
            
        # Calculate ROI if we have cost and revenue data
        if self.actual_cost and self.actual_cost > 0:
            # This would need revenue data from conversions
            # For now, we'll leave it to be calculated by the business logic
            pass
    
    def add_tag(self, tag: str):
        """Add tag to campaign"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from campaign"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list


class CampaignTarget(Base):
    """Campaign target (customer/lead) model"""
    
    __tablename__ = "campaign_targets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Target information
    target_type = Column(String(50), nullable=False)  # customer, lead, contact
    target_id = Column(UUID(as_uuid=True), nullable=False)  # ID of the target entity
    
    # Contact details
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    name = Column(String(255), nullable=False)
    
    # Campaign interaction
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Interaction counts
    open_count = Column(Integer, nullable=False, default=0)
    click_count = Column(Integer, nullable=False, default=0)
    
    # Status
    status = Column(String(50), nullable=False, default="pending")  # pending, sent, delivered, opened, clicked, converted, unsubscribed
    
    # Error handling
    error_message = Column(Text, nullable=True)
    bounce_reason = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    campaigns = relationship("Campaign", secondary=campaign_targets, back_populates="targets")
    
    def __repr__(self):
        return f"<CampaignTarget(name='{self.name}', status='{self.status}')>"


class CampaignMetric(Base):
    """Daily campaign performance metrics"""
    
    __tablename__ = "campaign_metrics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric date
    metric_date = Column(DateTime(timezone=True), nullable=False)
    
    # Daily metrics
    sent_count = Column(Integer, nullable=False, default=0)
    delivered_count = Column(Integer, nullable=False, default=0)
    opened_count = Column(Integer, nullable=False, default=0)
    clicked_count = Column(Integer, nullable=False, default=0)
    converted_count = Column(Integer, nullable=False, default=0)
    unsubscribed_count = Column(Integer, nullable=False, default=0)
    bounced_count = Column(Integer, nullable=False, default=0)
    
    # Daily costs
    cost = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Calculated rates
    delivery_rate = Column(Numeric(5, 2), nullable=True)
    open_rate = Column(Numeric(5, 2), nullable=True)
    click_rate = Column(Numeric(5, 2), nullable=True)
    conversion_rate = Column(Numeric(5, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'), nullable=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="metrics")
    
    def __repr__(self):
        return f"<CampaignMetric(campaign_id='{self.campaign_id}', date='{self.metric_date}')>"
    
    def calculate_rates(self):
        """Calculate daily performance rates"""
        if self.sent_count > 0:
            self.delivery_rate = (self.delivered_count / self.sent_count) * 100
            
        if self.delivered_count > 0:
            self.open_rate = (self.opened_count / self.delivered_count) * 100
            
        if self.opened_count > 0:
            self.click_rate = (self.clicked_count / self.opened_count) * 100
            
        if self.clicked_count > 0:
            self.conversion_rate = (self.converted_count / self.clicked_count) * 100