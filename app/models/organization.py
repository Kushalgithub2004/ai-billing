from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base_class import Base

class OrgRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    billing_email = Column(String, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    users = relationship("OrganizationMember", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True)
    role = Column(String, default=OrgRole.MEMBER, nullable=False)

    organization = relationship("Organization", back_populates="users")
    # user = relationship("User", back_populates="organizations") # Add this to User model if needed

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), index=True)
    key_prefix = Column(String, nullable=False)
    key_hash = Column(String, index=True, nullable=False)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    rate_limit_per_sec = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="api_keys")
