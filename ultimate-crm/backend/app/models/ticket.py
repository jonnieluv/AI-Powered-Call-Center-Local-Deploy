"""
Support ticket models for customer service and issue tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class TicketStatus(str, Enum):
    """Ticket status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_VENDOR = "waiting_vendor"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, Enum):
    """Ticket priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class Ticket(Base):
    """Support ticket model"""
    
    __tablename__ = "tickets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Status and priority
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolution_time_minutes = Column(Integer, nullable=True)
    
    # SLA tracking
    sla_breach_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    first_response_time_minutes = Column(Integer, nullable=True)
    
    # Customer satisfaction
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    satisfaction_comment = Column(Text, nullable=True)
    
    # Source and channel
    source = Column(String(100), nullable=True)  # email, phone, chat, web, etc.
    channel = Column(String(100), nullable=True)
    
    # Custom fields and tags
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('ticket_categories.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tickets")
    created_by = relationship("User", foreign_keys=[created_by_id])
    category = relationship("TicketCategory", back_populates="tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="ticket")
    
    def __repr__(self):
        return f"<Ticket(number='{self.ticket_number}', subject='{self.subject}')>"
    
    def calculate_resolution_time(self):
        """Calculate ticket resolution time"""
        if self.resolved_at and self.created_at:
            duration = self.resolved_at - self.created_at
            self.resolution_time_minutes = int(duration.total_seconds() / 60)
        return self.resolution_time_minutes
    
    def calculate_first_response_time(self):
        """Calculate first response time"""
        if self.first_response_at and self.created_at:
            duration = self.first_response_at - self.created_at
            self.first_response_time_minutes = int(duration.total_seconds() / 60)
        return self.first_response_time_minutes
    
    def add_tag(self, tag: str):
        """Add tag to ticket"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from ticket"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list


class TicketCategory(Base):
    """Support ticket categories"""
    
    __tablename__ = "ticket_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Category information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # SLA configuration
    sla_hours = Column(Integer, nullable=True)  # Hours to resolve
    first_response_hours = Column(Integer, nullable=True)  # Hours for first response
    
    # Auto-assignment
    auto_assign_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    auto_assign_to = relationship("User", foreign_keys=[auto_assign_to_id])
    tickets = relationship("Ticket", back_populates="category")
    
    def __repr__(self):
        return f"<TicketCategory(name='{self.name}')>"


class TicketComment(Base):
    """Ticket comments and updates"""
    
    __tablename__ = "ticket_comments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Comment content
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), nullable=False, default="comment")  # comment, status_change, assignment, etc.
    
    # Visibility
    is_internal = Column(Boolean, default=False, nullable=False)  # Internal comments not visible to customer
    is_system = Column(Boolean, default=False, nullable=False)  # System-generated comments
    
    # Attachments
    attachments = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('tickets.id'), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<TicketComment(ticket_id='{self.ticket_id}', type='{self.comment_type}')>"