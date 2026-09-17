# servicios/admin.py — Brillo-Boom
from models import Usuario, Producto, Pedido

def dashboard_stats():
    return {
        'total_productos':   Producto.query.count(),
        'total_usuarios':    Usuario.query.filter_by(id_tipou=2).count(),
        'agotados':          Producto.query.filter(Producto.stock <= 0).all(),
        'pedidos_recientes': Pedido.query.order_by(Pedido.fecha.desc()).limit(10).all(),
    }
