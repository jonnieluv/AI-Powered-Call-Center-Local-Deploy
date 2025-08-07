"""
User models for authentication and authorization
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

from app.core.database import Base


# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)


class User(Base):
    """User model for system authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Business information
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    employee_id = Column(String(50), nullable=True, unique=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Preferences
    preferences = Column(JSONB, nullable=True, default={})
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_customers = relationship("Customer", back_populates="created_by", foreign_keys="Customer.created_by_id")
    assigned_leads = relationship("Lead", back_populates="assigned_to", foreign_keys="Lead.assigned_to_id")
    created_opportunities = relationship("Opportunity", back_populates="created_by", foreign_keys="Opportunity.created_by_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_to", foreign_keys="Ticket.assigned_to_id")
    activities = relationship("Activity", back_populates="user", foreign_keys="Activity.user_id")
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has specific permission"""
        for role in self.roles:
            if permission_name in role.permissions:
                return True
        return False


class Role(Base):
    """Role model for role-based access control"""
    
    __tablename__ = "roles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Role information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Role configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_system_role = Column(Boolean, default=False, nullable=False)  # Cannot be deleted
    
    # Permissions (stored as JSON array)
    permissions = Column(JSONB, nullable=False, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role(name='{self.name}', display_name='{self.display_name}')>"
    
    def add_permission(self, permission: str):
        """Add permission to role"""
        if permission not in self.permissions:
            self.permissions = self.permissions + [permission]
    
    def remove_permission(self, permission: str):
        """Remove permission from role"""
        if permission in self.permissions:
            permissions_list = list(self.permissions)
            permissions_list.remove(permission)
            self.permissions = permissions_list
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions


class UserRole(Base):
    """Explicit user-role relationship with additional metadata"""
    
    __tablename__ = "user_role_assignments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    
    # Assignment metadata
    assigned_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    
    def __repr__(self):
        return f"<UserRole(user_id='{self.user_id}', role_id='{self.role_id}')>"
    
    @property
    def is_expired(self):
        """Check if role assignment is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


# Default system roles and permissions
SYSTEM_ROLES = {
    "super_admin": {
        "display_name": "Super Administrator",
        "description": "Full system access",
        "permissions": [
            "system.manage",
            "users.manage",
            "roles.manage",
            "customers.manage",
            "leads.manage",
            "opportunities.manage",
            "campaigns.manage",
            "tickets.manage",
            "reports.view",
            "settings.manage"
        ]
    },
    "admin": {
        "display_name": "Administrator",
        "description": "Administrative access",
        "permissions": [
            "users.view",
            "users.create",
            "users.update",
            "customers.manage",
            "leads.manage",
            "opportunities.manage",
            "campaigns.manage",
            "tickets.manage",
            "reports.view"
        ]
    },
    "sales_manager": {
        "display_name": "Sales Manager",
        "description": "Sales team management",
        "permissions": [
            "leads.manage",
            "opportunities.manage",
            "customers.manage",
            "activities.manage",
            "reports.sales.view",
            "users.sales.view"
        ]
    },
    "sales_rep": {
        "display_name": "Sales Representative",
        "description": "Sales activities",
        "permissions": [
            "leads.view",
            "leads.update",
            "opportunities.view",
            "opportunities.update",
            "customers.view",
            "customers.update",
            "activities.manage"
        ]
    },
    "marketing_manager": {
        "display_name": "Marketing Manager",
        "description": "Marketing team management",
        "permissions": [
            "campaigns.manage",
            "leads.view",
            "customers.view",
            "reports.marketing.view",
            "content.manage"
        ]
    },
    "support_manager": {
        "display_name": "Support Manager",
        "description": "Customer support management",
        "permissions": [
            "tickets.manage",
            "customers.view",
            "knowledge.manage",
            "reports.support.view"
        ]
    },
    "support_agent": {
        "display_name": "Support Agent",
        "description": "Customer support",
        "permissions": [
            "tickets.view",
            "tickets.update",
            "customers.view",
            "knowledge.view"
        ]
    },
    "viewer": {
        "display_name": "Viewer",
        "description": "Read-only access",
        "permissions": [
            "customers.view",
            "leads.view",
            "opportunities.view",
            "tickets.view",
            "reports.basic.view"
        ]
    }
}