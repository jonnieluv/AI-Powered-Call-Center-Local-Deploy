"""
Product and pricing models for catalog management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from enum import Enum

from app.core.database import Base


class ProductStatus(str, Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class PricingType(str, Enum):
    """Pricing type enumeration"""
    FIXED = "fixed"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"
    SUBSCRIPTION = "subscription"


class Product(Base):
    """Product catalog model"""
    
    __tablename__ = "products"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Status
    status = Column(SQLEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)
    
    # Pricing
    base_price = Column(Numeric(15, 2), nullable=False)
    cost_price = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    pricing_type = Column(SQLEnum(PricingType), nullable=False, default=PricingType.FIXED)
    
    # Inventory
    track_inventory = Column(Boolean, default=False, nullable=False)
    stock_quantity = Column(Integer, nullable=True)
    low_stock_threshold = Column(Integer, nullable=True)
    
    # Physical properties
    weight = Column(Numeric(10, 2), nullable=True)
    dimensions = Column(JSONB, nullable=True, default={})  # length, width, height
    
    # Digital properties
    is_digital = Column(Boolean, default=False, nullable=False)
    download_url = Column(String(500), nullable=True)
    license_key_required = Column(Boolean, default=False, nullable=False)
    
    # SEO and marketing
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    keywords = Column(JSONB, nullable=True, default=[])
    
    # Media
    images = Column(JSONB, nullable=True, default=[])
    videos = Column(JSONB, nullable=True, default=[])
    
    # Features and specifications
    features = Column(JSONB, nullable=True, default=[])
    specifications = Column(JSONB, nullable=True, default={})
    
    # Custom fields and tags
    custom_fields = Column(JSONB, nullable=True, default={})
    tags = Column(JSONB, nullable=True, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    category_id = Column(UUID(as_uuid=True), ForeignKey('product_categories.id'), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    created_by = relationship("User")
    pricing_tiers = relationship("PricingTier", back_populates="product", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", secondary="opportunity_products", back_populates="products")
    
    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}')>"
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        if self.track_inventory and self.low_stock_threshold:
            return self.stock_quantity <= self.low_stock_threshold
        return False
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        if self.track_inventory:
            return self.stock_quantity <= 0
        return False
    
    def add_tag(self, tag: str):
        """Add tag to product"""
        if tag not in self.tags:
            self.tags = self.tags + [tag]
    
    def remove_tag(self, tag: str):
        """Remove tag from product"""
        if tag in self.tags:
            tags_list = list(self.tags)
            tags_list.remove(tag)
            self.tags = tags_list
    
    def add_feature(self, feature: str):
        """Add feature to product"""
        if feature not in self.features:
            self.features = self.features + [feature]
    
    def remove_feature(self, feature: str):
        """Remove feature from product"""
        if feature in self.features:
            features_list = list(self.features)
            features_list.remove(feature)
            self.features = features_list


class ProductCategory(Base):
    """Product category model"""
    
    __tablename__ = "product_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    
    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey('product_categories.id'), nullable=True)
    level = Column(Integer, nullable=False, default=0)
    path = Column(String(500), nullable=True)  # Materialized path for hierarchy
    
    # Display
    image_url = Column(String(500), nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    created_by = relationship("User")
    parent = relationship("ProductCategory", remote_side=[id])
    children = relationship("ProductCategory")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<ProductCategory(name='{self.name}', level={self.level})>"


class PricingTier(Base):
    """Pricing tier model for tiered and usage-based pricing"""
    
    __tablename__ = "pricing_tiers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tier information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Tier conditions
    min_quantity = Column(Integer, nullable=False, default=1)
    max_quantity = Column(Integer, nullable=True)  # NULL means unlimited
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False)
    setup_fee = Column(Numeric(15, 2), nullable=True, default=0)
    recurring_fee = Column(Numeric(15, 2), nullable=True, default=0)
    
    # Billing
    billing_period = Column(String(50), nullable=True)  # monthly, yearly, one-time
    billing_cycle = Column(Integer, nullable=True, default=1)  # Every N periods
    
    # Features and limits
    features = Column(JSONB, nullable=True, default=[])
    limits = Column(JSONB, nullable=True, default={})
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_popular = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="pricing_tiers")
    
    def __repr__(self):
        return f"<PricingTier(name='{self.name}', price={self.unit_price})>"
    
    def calculate_price(self, quantity: int):
        """Calculate price for given quantity"""
        if self.max_quantity and quantity > self.max_quantity:
            return None  # Quantity exceeds tier limit
        
        if quantity < self.min_quantity:
            return None  # Quantity below tier minimum
        
        base_price = quantity * self.unit_price
        total_price = base_price + (self.setup_fee or 0)
        
        return total_price