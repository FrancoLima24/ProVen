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
    alerta_vencimiento = db.Column(db.Boolean, default=False, nullable=False)  # Nuevo campo para alertas
    ventas_acumuladas = db.Column(db.Integer, default=0, nullable=False)  # Ventas totales para el resumen de ventas


class Stock(db.Model):
    __tablename__ = 'Stock'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    fecha_ingreso = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    vendido = db.Column(db.Boolean, default=False, nullable=False)
    proximo_a_vencer = db.Column(db.Boolean, default=False, nullable=False)  # Campo para manejar alertas de vencimiento


class Venta(db.Model):
    __tablename__ = 'Venta'
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    id_stock = db.Column(db.Integer, db.ForeignKey('Stock.id'), nullable=False)
    monto_total = db.Column(db.Float, nullable=False)  # Nuevo campo para el monto total de la venta


class PrecioHistorico(db.Model):
    __tablename__ = 'PrecioHistorico'  # Cambia el nombre para coincidir con la tabla existente
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id'), nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
