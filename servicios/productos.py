# servicios/productos.py — Brillo-Boom
from models import db, Producto

def obtener_todos(marca_id=None, busqueda=None):
    q = Producto.query
    if marca_id:  q = q.filter_by(id_empresa_productos=marca_id)
    if busqueda:  q = q.filter(Producto.nombre.ilike(f'%{busqueda}%'))
    return q.all()

def obtener_por_id(id_producto):  return Producto.query.get_or_404(id_producto)

def _leer_imagen(form):
    """Si el formulario trae un archivo de imagen nuevo, devuelve (datos, tipo)."""
    archivo = form.imagen.data
    if archivo and getattr(archivo, 'filename', ''):
        datos = archivo.read()
        tipo  = archivo.mimetype or 'image/jpeg'
        return datos, tipo
    return None, None

def crear(form, id_empresa):
    datos, tipo = _leer_imagen(form)
    p = Producto(nombre=form.nombre.data, descripcion=form.descripcion.data,
                 precio=float(form.precio.data), stock=int(form.stock.data),
                 imagen_datos=datos, imagen_tipo=tipo,
                 id_empresa_productos=id_empresa)
    db.session.add(p); db.session.commit(); return p

def actualizar(id_producto, form):
    p = Producto.query.get_or_404(id_producto)
    p.nombre = form.nombre.data; p.descripcion = form.descripcion.data
    p.precio = float(form.precio.data); p.stock = int(form.stock.data)
    datos, tipo = _leer_imagen(form)
    if datos:  # solo se reemplaza la imagen si se subió una nueva
        p.imagen_datos = datos
        p.imagen_tipo  = tipo
    p.id_empresa_productos = form.id_empresa_productos.data
    db.session.commit(); return p

def eliminar(id_producto):
    p = Producto.query.get_or_404(id_producto)
    
    # En vez de borrar los pedidos, solo desvincular el producto
    # poniendo el nombre del producto en una columna de respaldo
    for pedido in p.pedidos:
        pedido.nombre_producto = p.nombre  # guardamos el nombre
        pedido.id_producto = None          # desvincular

    db.session.delete(p)
    db.session.commit()