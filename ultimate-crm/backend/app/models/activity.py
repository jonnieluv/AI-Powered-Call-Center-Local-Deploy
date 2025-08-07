"""
Activity models for tracking all customer interactions and tasks
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class ActivityType(str, Enum):
    """Activity type enumeration"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    SMS = "sms"
    SOCIAL = "social"
    WEBINAR = "webinar"
    DEMO = "demo"
    PROPOSAL = "proposal"
    CONTRACT = "contract"
    PAYMENT = "payment"
    SUPPORT = "support"


class ActivityStatus(str, Enum):
    """Activity status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class ActivityPriority(str, Enum):
    """Activity priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Activity(Base):
    """Activity model for tracking all customer interactions"""
    
    __tablename__ = "activities"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    
    # Status and priority
    status = Column(SQLEnum(ActivityStatus), nullable=False, default=ActivityStatus.PLANNED)
    priority = Column(SQLEnum(ActivityPriority), nullable=False, default=ActivityPriority.MEDIUM)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Location and method
    location = Column(String(255), nullable=True)
    meeting_url = Column(String(500), nullable=True)
    
    # Results and outcome
    outcome = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    
    # Communication details
    subject = Column(String(255), nullable=True)  # For emails
    body = Column(Text, nullable=True)  # For emails/messages
    attachments = Column(JSONB, nullable=True, default=[])
    
    # Tracking
    is_billable = Column(Boolean, default=False, nullable=False)
    billable_hours = Column(Integer, nullable=True)
    
    # Custom fields
    custom_fields = Column(JSONB, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey('contacts.id'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunities.id'), nullable=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey('tickets.id'), nullable=True)
    activity_type_id = Column(UUID(as_uuid=True), ForeignKey('activity_types.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    customer = relationship("Customer", back_populates="activities")
    contact = relationship("Contact", back_populates="activities")
    lead = relationship("Lead", back_populates="activities")
    opportunity = relationship("Opportunity", back_populates="activities")
    ticket = relationship("Ticket", back_populates="activities")
    activity_type_config = relationship("ActivityTypeConfig")
    
    def __repr__(self):
        return f"<Activity(title='{self.title}', type='{self.activity_type}')>"
    
    @property
    def is_overdue(self):
        """Check if activity is overdue"""
        if self.scheduled_at and self.status in [ActivityStatus.PLANNED, ActivityStatus.IN_PROGRESS]:
            from datetime import datetime
            return datetime.utcnow() > self.scheduled_at
        return False
    
    def calculate_duration(self):
        """Calculate activity duration"""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
        return self.duration_minutes
    
    def mark_completed(self, outcome: str = None):
        """Mark activity as completed"""
        self.status = ActivityStatus.COMPLETED
        self.completed_at = func.now()
        if outcome:
            self.outcome = outcome
        self.calculate_duration()


class ActivityTypeConfig(Base):
    """Configuration for different activity types"""
    
    __tablename__ = "activity_types"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Type information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    default_duration_minutes = Column(Integer, nullable=True)
    is_billable_default = Column(Boolean, default=False, nullable=False)
    
    # Automation settings
    auto_create_follow_up = Column(Boolean, default=False, nullable=False)
    follow_up_days = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<ActivityTypeConfig(name='{self.name}', display_name='{self.display_name}')>"


class Task(Base):
    """Task model for action items and follow-ups"""
    
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and priority
    status = Column(SQLEnum(ActivityStatus), nullable=False, default=ActivityStatus.PLANNED)
    priority = Column(SQLEnum(ActivityPriority), nullable=False, default=ActivityPriority.MEDIUM)
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminder_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    progress_percent = Column(Integer, nullable=False, default=0)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    
    # Assignment
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)  # daily, weekly, monthly, etc.
    
    # Custom fields
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunities.id'), nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=True)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    customer = relationship("Customer")
    lead = relationship("Lead")
    opportunity = relationship("Opportunity")
    parent_task = relationship("Task", remote_side=[id])
    subtasks = relationship("Task")
    
    def __repr__(self):
        return f"<Task(title='{self.title}', status='{self.status}')>"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != ActivityStatus.COMPLETED:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    def mark_completed(self):
        """Mark task as completed"""
        self.status = ActivityStatus.COMPLETED
        self.completed_at = func.now()
        self.progress_percent = 100
    
    def add_tag(self, tag: str):
        """Add tag to task"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from task"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list