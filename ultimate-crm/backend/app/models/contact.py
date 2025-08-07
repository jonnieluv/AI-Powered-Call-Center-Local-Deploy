"""
Contact models for managing customer contacts and communication methods
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class ContactType(str, Enum):
    """Contact type enumeration"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BILLING = "billing"
    TECHNICAL = "technical"
    DECISION_MAKER = "decision_maker"


class ContactMethodType(str, Enum):
    """Contact method type enumeration"""
    EMAIL = "email"
    PHONE = "phone"
    MOBILE = "mobile"
    FAX = "fax"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    SKYPE = "skype"
    WHATSAPP = "whatsapp"


class Contact(Base):
    """Customer contact person model"""
    
    __tablename__ = "contacts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Contact type
    contact_type = Column(SQLEnum(ContactType), nullable=False, default=ContactType.PRIMARY)
    
    # Primary contact information
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Preferences
    preferred_contact_method = Column(String(50), nullable=True)
    preferred_language = Column(String(10), nullable=True, default="en")
    timezone = Column(String(50), nullable=True, default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Custom fields
    custom_fields = Column(JSONB, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="contacts")
    created_by = relationship("User")
    contact_methods = relationship("ContactMethod", back_populates="contact", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="contact")
    
    def __repr__(self):
        return f"<Contact(name='{self.first_name} {self.last_name}', customer_id='{self.customer_id}')>"
    
    @property
    def full_name(self):
        """Get contact's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get display name with job title"""
        name = self.full_name
        if self.job_title:
            name += f" ({self.job_title})"
        return name


class ContactMethod(Base):
    """Contact methods for different communication channels"""
    
    __tablename__ = "contact_methods"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Method information
    method_type = Column(SQLEnum(ContactMethodType), nullable=False)
    value = Column(String(255), nullable=False)
    label = Column(String(100), nullable=True)  # e.g., "Work", "Personal", "Mobile"
    
    # Status and preferences
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    opt_in = Column(Boolean, default=True, nullable=False)  # For marketing communications
    
    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    contact_id = Column(UUID(as_uuid=True), ForeignKey('contacts.id'), nullable=False)
    
    # Relationships
    contact = relationship("Contact", back_populates="contact_methods")
    
    def __repr__(self):
        return f"<ContactMethod(type='{self.method_type}', value='{self.value}')>"