# models.py — Brillo-Boom  (tablas de la base de datos)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Tipo_Usuario(db.Model):
    __tablename__ = 'tipos_usuarios'
    id_tipou = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(40), nullable=False)
    usuarios = db.relationship('Usuario', backref='tipo', lazy=True)
    def __repr__(self): return f'<Tipo_Usuario {self.nombre}>'

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(40),  nullable=False)
    clave      = db.Column(db.String(256), nullable=False)
    email      = db.Column(db.String(50),  unique=True, nullable=False)
    direccion  = db.Column(db.String(100), nullable=False)
    telefono   = db.Column(db.String(20),  nullable=False)
    id_tipou   = db.Column(db.Integer, db.ForeignKey('tipos_usuarios.id_tipou'), nullable=False)
    pedidos    = db.relationship('Pedido', backref='usuario', lazy=True)
    foto_url   = db.Column(db.String(200), nullable=True)
    def get_id(self):            return str(self.id_usuario)
    def set_password(self, pw):  self.clave = generate_password_hash(pw)
    def check_password(self, pw):return check_password_hash(self.clave, pw)
    def es_admin(self):          return self.id_tipou == 1
    def __repr__(self): return f'<Usuario {self.nombre}>'

class Empresa_Producto(db.Model):
    __tablename__ = 'empresas_productos'
    id_empresa_productos = db.Column(db.Integer, primary_key=True)
    nombre               = db.Column(db.String(40), nullable=False)
    productos            = db.relationship('Producto', backref='empresa', lazy=True)
    def __repr__(self): return f'<Empresa_Producto {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto          = db.Column(db.Integer, primary_key=True)
    nombre               = db.Column(db.String(40),  nullable=False)
    descripcion          = db.Column(db.String(200), nullable=False)
    precio               = db.Column(db.Float,   nullable=False, default=0.0)
    stock                = db.Column(db.Integer, nullable=False, default=0)
    imagen_url           = db.Column(db.String(200), nullable=True)
    imagen_datos         = db.Column(db.LargeBinary(length=(2**24)-1), nullable=True)
    imagen_tipo          = db.Column(db.String(50), nullable=True)
    id_empresa_productos = db.Column(db.Integer,
                           db.ForeignKey('empresas_productos.id_empresa_productos'), nullable=False)
    pedidos  = db.relationship('Pedido', backref='producto', lazy=True)
    def agotado(self): return self.stock <= 0
    def tiene_imagen(self): return bool(self.imagen_datos)
    def __repr__(self): return f'<Producto {self.nombre}>'

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido        = db.Column(db.Integer, primary_key=True)
    cantidad         = db.Column(db.Integer, nullable=False)
    fecha            = db.Column(db.Date,    nullable=False)
    valor            = db.Column(db.Float,   nullable=False)
    nombre_producto  = db.Column(db.String(40), nullable=True)  # ← agrega esta línea
    id_producto      = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=True)  # ← cambia nullable=False a True
    id_usuario       = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'),  nullable=False)
    pagos            = db.relationship('Pago', backref='pedido', lazy=True)

class Medio_de_Pago(db.Model):
    __tablename__ = 'medios_de_pagos'
    id_medio = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(20), nullable=False)
    pagos    = db.relationship('Pago', backref='medio', lazy=True)
    def __repr__(self): return f'<Medio_de_Pago {self.nombre}>'

class Pago(db.Model):
    __tablename__ = 'pagos'
    id_pago   = db.Column(db.Integer, primary_key=True)
    valor     = db.Column(db.Float,   nullable=False)
    id_medio  = db.Column(db.Integer, db.ForeignKey('medios_de_pagos.id_medio'), nullable=False)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'),        nullable=False)
    def __repr__(self): return f'<Pago {self.id_pago}>'

class Reporte(db.Model):
    __tablename__ = 'reportes'
    id_reporte      = db.Column(db.Integer, primary_key=True)
    tipo            = db.Column(db.String(50), nullable=False)  # 'usuarios', 'productos', 'pedidos'
    archivo         = db.Column(db.LargeBinary, nullable=False)  # el PDF en bytes
    nombre_archivo  = db.Column(db.String(100), nullable=False)
    fecha_generacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario_admin = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    admin = db.relationship('Usuario', backref='reportes')
