from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Producto(db.Model):
    __tablename__ = 'Producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    stock = db.relationship('Stock', backref='producto', lazy=True)
    ventas = db.relationship('Venta', backref='producto', lazy=True)
    promociones = db.relationship('Promocion', backref='producto', lazy=True)  # Relación con Promociones

class Stock(db.Model):
    __tablename__ = 'Stock'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    fecha_ingreso = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    vendido = db.Column(db.Boolean, default=False, nullable=False)

class Venta(db.Model):
    __tablename__ = 'Venta'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    id_stock = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)

class PrecioHistorico(db.Model):
    __tablename__ = 'PrecioHistorico'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Promocion(db.Model):
    __tablename__ = 'Promocion'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descuento = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

class ConfiguracionUsuario(db.Model):
    __tablename__ = 'ConfiguracionUsuario'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    preferencias_reportes = db.Column(db.String(200), nullable=True)
    recibir_alertas = db.Column(db.Boolean, default=True)
