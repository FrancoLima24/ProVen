from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
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


class TotalesNegocio(db.Model):
    __tablename__ = 'TotalesNegocio'
    id = db.Column(db.Integer, primary_key=True)
    total_ventas = db.Column(db.Float, nullable=False)
    productos_vendidos = db.Column(db.Integer, nullable=False)
    stock_disponible = db.Column(db.Integer, nullable=False)
    promociones_activas = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, total_ventas, productos_vendidos, stock_disponible, promociones_activas):
        self.total_ventas = total_ventas
        self.productos_vendidos = productos_vendidos
        self.stock_disponible = stock_disponible
        self.promociones_activas = promociones_activas
        
class Usuarios(db.Model):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)  # Nombre de usuario, no un email
    password_hash = db.Column(db.String(256), nullable=False)  # Contraseña hasheada
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id'), nullable=False)  # Relación con la tabla de roles

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Métodos requeridos por Flask-Login
    @property
    def is_authenticated(self):
        return True  # Siempre autenticado

    @property
    def is_active(self):
        return True  # Activo por defecto; puedes agregar lógica aquí

    @property
    def is_anonymous(self):
        return False  # Nunca anónimo en este caso
    
    def get_id(self):
        return str(self.id)  # Devuelve el ID del usuario como una cadena

class Roles(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # Nombre del rol
    usuarios = db.relationship('Usuarios', backref='rol', lazy=True, foreign_keys=[Usuarios.id_rol])
# Asegúrate de que el nombre sea 'Usuarios'
