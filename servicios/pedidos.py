# servicios/pedidos.py — Brillo-Boom
# También contiene: medios_de_pagos, pagos, tipos_usuarios
from models import db, Pedido, Producto, Pago, Medio_de_Pago, Tipo_Usuario
from datetime import datetime

# ─── PEDIDOS ────────────────────────────────────────────────
def crear_desde_carrito(id_usuario, carrito_session):
    """carrito_session = {'id_prod': cantidad, ...}"""
    pedidos_creados = []
    for id_prod_str, cantidad in carrito_session.items():
        p = Producto.query.get(int(id_prod_str))
        if not p: continue
        if p.stock < cantidad:
            return None, f'Stock insuficiente para "{p.nombre}"'
        pedido = Pedido(cantidad=cantidad, fecha=datetime.now(),
                        valor=p.precio * cantidad,
                        id_producto=p.id_producto, id_usuario=id_usuario)
        p.stock -= cantidad
        db.session.add(pedido)
        pedidos_creados.append(pedido)
    db.session.commit()
    return pedidos_creados, None

def obtener_por_usuario(id_usuario):
    return Pedido.query.filter_by(id_usuario=id_usuario)\
                       .order_by(Pedido.fecha.desc()).all()

def obtener_todos():
    return Pedido.query.order_by(Pedido.fecha.desc()).all()

# ─── MEDIOS DE PAGO ─────────────────────────────────────────
def obtener_medios():   return Medio_de_Pago.query.all()

def crear_medio(nombre):
    m = Medio_de_Pago(nombre=nombre)
    db.session.add(m); db.session.commit(); return m

# ─── PAGOS ──────────────────────────────────────────────────
def registrar_pago(valor, id_medio, id_pedido):
    pago = Pago(valor=valor, id_medio=id_medio, id_pedido=id_pedido)
    db.session.add(pago); db.session.commit(); return pago

def obtener_pagos():    return Pago.query.all()

# ─── TIPOS DE USUARIO ───────────────────────────────────────
def obtener_tipos():    return Tipo_Usuario.query.all()
