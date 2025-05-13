# models/purchase_order.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Text, Enum
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import relationship
import enum

# Definición del Enum (opcional pero útil para validación en Python)
class OrderStatus(enum.Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED'

