"""
Invoice and payment models for financial management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class InvoiceStatus(str, Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CHECK = "check"
    CASH = "cash"
    WIRE_TRANSFER = "wire_transfer"


class Invoice(Base):
    """Invoice model for billing and payments"""
    
    __tablename__ = "invoices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0)
    due_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    # Currency and tax
    currency = Column(String(3), nullable=False, default="USD")
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    
    # Dates
    issue_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    sent_date = Column(DateTime(timezone=True), nullable=True)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    
    # Terms and conditions
    payment_terms = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Billing address
    billing_name = Column(String(255), nullable=True)
    billing_address = Column(Text, nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(100), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_country = Column(String(100), nullable=True)
    
    # Purchase order
    po_number = Column(String(100), nullable=True)
    
    # Custom fields
    custom_fields = Column(JSONB, nullable=True, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('opportunities.id'), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    opportunity = relationship("Opportunity")
    created_by = relationship("User")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', total={self.total_amount})>"
    
    def calculate_totals(self):
        """Calculate invoice totals from items"""
        self.subtotal = sum(item.total_amount for item in self.items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.due_amount = self.total_amount - self.paid_amount
    
    def add_payment(self, amount: float):
        """Add payment amount to invoice"""
        self.paid_amount += amount
        self.due_amount = self.total_amount - self.paid_amount
        
        # Update status based on payment
        if self.due_amount <= 0:
            self.status = InvoiceStatus.PAID
            self.paid_date = func.now()
        elif self.paid_amount > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status in [InvoiceStatus.SENT, InvoiceStatus.VIEWED, InvoiceStatus.PARTIALLY_PAID]:
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False


class InvoiceItem(Base):
    """Invoice line item model"""
    
    __tablename__ = "invoice_items"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Item information
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), nullable=True, default=0)
    discount_amount = Column(Numeric(15, 2), nullable=True, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tax_rate = Column(Numeric(5, 2), nullable=True, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Sort order
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<InvoiceItem(description='{self.description}', total={self.total_amount})>"
    
    def calculate_total(self):
        """Calculate item total including discounts and tax"""
        subtotal = self.quantity * self.unit_price
        
        # Apply discount
        if self.discount_percent:
            self.discount_amount = subtotal * (self.discount_percent / 100)
        
        amount_after_discount = subtotal - (self.discount_amount or 0)
        
        # Calculate tax
        if self.tax_rate:
            self.tax_amount = amount_after_discount * (self.tax_rate / 100)
        
        self.total_amount = amount_after_discount + (self.tax_amount or 0)
        return self.total_amount


class Payment(Base):
    """Payment model for tracking invoice payments"""
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Payment information
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Status and method
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # Payment details
    reference_number = Column(String(255), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    gateway_response = Column(JSONB, nullable=True, default={})
    
    # Dates
    payment_date = Column(DateTime(timezone=True), nullable=False)
    processed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Fee information
    gateway_fee = Column(Numeric(15, 2), nullable=True, default=0)
    net_amount = Column(Numeric(15, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Payment(number='{self.payment_number}', amount={self.amount})>"
    
    def calculate_net_amount(self):
        """Calculate net amount after gateway fees"""
        self.net_amount = self.amount - (self.gateway_fee or 0)
        return self.net_amount