from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
import os
from dotenv import load_dotenv

load_dotenv()

serializer = Serializer(os.getenv("SECRET_KEY") or os.urandom(
    32), salt='Email Confirmation')


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(120), unique=True)
    password_hash = Column(String(256))
    is_admin = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    is_supplier = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    def __init__(self, name=None, email=None, is_admin=False, is_manager=False, is_supplier=False, is_verified=False):
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.is_manager = is_manager
        self.is_supplier = is_supplier
        self.is_verified = is_verified

    def __repr__(self):
        return '<User %r>' % (self.email)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_manager": self.is_manager,
            "is_supplier": self.is_supplier,
            "is_verified": self.is_verified
        }

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        return serializer.dumps({'confirm': self.id})

    @staticmethod
    def load_token(token):
        data = serializer.loads(token)
        return data.get('confirm', None)

    def get_role(self):
        if self.is_admin:
            return "Admin"
        elif self.is_manager:
            return "Manager"
        else:
            return "Supplier"

# Send email to someone for receiving an order to fullfil and vice versa when an order has been fullfiled and add it automatically to invetory


class Order(UserMixin, db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)
    delivered = Column(Boolean, default=False)
    delivery_date = Column(DateTime, nullable=True)
    supplier_id = Column(Integer, ForeignKey('users.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    supplier = relationship("User", foreign_keys=[
        supplier_id], backref="orders")
    owner = relationship("User", foreign_keys=[
                         owner_id], backref="own_orders")
    item = relationship("Item", foreign_keys=[
                        item_id], backref="in_orders")

    def __init__(self, item_id=None, quantity=0, unit_price=0, total_price=0, supplier_id=None, owner_id=None):
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.supplier_id = supplier_id
        self.owner_id = owner_id

    def __repr__(self):
        return '<Comment %r>' % (self.comment)

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "paid": self.paid,
            "supplier_id": self.supplier_id,
            "supplier": self.supplier.to_dict(),
            "item": self.item.to_dict(),
            "owner_id": self.owner.to_dict(),
            "owner": self.owner.to_dict()
        }


class Item(UserMixin, db.Model):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    description = Column(String(256))

    def __init__(self, name=None, description=None):
        self.name = name.upper()
        self.description = description

    def __repr__(self):
        return f'<Item {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class Inventory(UserMixin, db.Model):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", foreign_keys=[
                         owner_id], backref="inventory")
    item = relationship("Item", foreign_keys=[item_id])

    def __init__(self, item_id=None, quantity=0, unit_price=None, owner_id=None):
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.owner_id = owner_id

    def __repr__(self):
        return f'<Inventory {self.item_type, self.quantity, self.unit_price}>'

    def to_dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "owner_id": self.owner_id,
            "owner": self.owner.to_dict()
        }

# Send email to someone for receiving a payment for the order so they can fullfil it


class Payment(UserMixin, db.Model):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    method = Column(String(80))
    payment_date = Column(DateTime, nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    debitor_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    order = relationship("Order", foreign_keys=[
                         order_id], backref="payments", cascade="all, delete")
    debitor = relationship("User", foreign_keys=[
                           debitor_id], backref="payments", cascade="all, delete")
    receiver = relationship("User", foreign_keys=[
                            receiver_id], backref="received_payments", cascade="all, delete")

    def __init__(self, payment_date=None, amount=0, method=None, order_id=None, debitor_id=None, receiver_id=None):
        self.payment_date = payment_date
        self.amount = amount
        self.method = method
        self.order_id = order_id
        self.debitor_id = debitor_id
        self.receiver_id = receiver_id

    def __repr__(self):
        return f'<Payment {self.payment_type, self.amount, self.method}>'

    def to_dict(self):
        return {
            "id": self.id,
            "payment_type": self.payment_type,
            "amount": self.amount,
            "method": self.method,
            "order_id": self.order_id,
            "debitor_id": self.debitor_id,
            "order": self.order.to_dict(),
            "debitor": self.debitor.to_dict(),
            "receiver": self.receiver.to_dict()
        }
