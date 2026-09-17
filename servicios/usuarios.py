# servicios/usuarios.py — Brillo-Boom
from models import db, Usuario

def registrar_usuario(form):
    if Usuario.query.filter_by(email=form.email.data).first():
        return None, 'El correo ya está registrado.'
    if Usuario.query.filter_by(telefono=form.telefono.data).first():
        return None, 'El teléfono ya está registrado.'
    u = Usuario(nombre=form.nombre.data, email=form.email.data,
                telefono=form.telefono.data, direccion=form.direccion.data, id_tipou=2)
    u.set_password(form.password.data)
    db.session.add(u)
    db.session.commit()
    return u, None

def obtener_por_email(email):    return Usuario.query.filter_by(email=email).first()
def obtener_por_telefono(tel):   return Usuario.query.filter_by(telefono=tel).first()
def obtener_por_id(id_usuario):  return Usuario.query.get(id_usuario)
def listar_usuarios():           return Usuario.query.all()
def total_clientes():            return Usuario.query.filter_by(id_tipou=2).count()
