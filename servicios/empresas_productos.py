# servicios/empresas_productos.py — Brillo-Boom
from models import db, Empresa_Producto

def obtener_todas():             return Empresa_Producto.query.all()
def obtener_por_id(id_empresa):  return Empresa_Producto.query.get_or_404(id_empresa)
def crear(nombre):
    m = Empresa_Producto(nombre=nombre)
    db.session.add(m); db.session.commit(); return m
