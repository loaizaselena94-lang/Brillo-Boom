# app.py — Brillo-Boom
# Rutas principales + arranque de la aplicación Flask
from flask import (Flask, render_template, redirect, url_for,
                   flash, request, jsonify, session, abort, Response)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from functools import wraps


from config import config
from models import db, Usuario, Tipo_Usuario, Producto, Empresa_Producto, Medio_de_Pago, Pedido
from forms import LoginForm, RegistroForm, ProductoForm

import servicios.usuarios          as svc_usr
import servicios.admin             as svc_adm
import servicios.productos         as svc_prod
import servicios.empresas_productos as svc_emp
import servicios.pedidos           as svc_ped
import servicios.reportes          as svc_rep
import mimetypes
mimetypes.add_type('image/svg+xml', '.svg')
# ── Inicialización ────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(config['default'])
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view            = 'login'
login_manager.login_message         = 'Inicia sesión para continuar.'
login_manager.login_message_category= 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ── Decorador solo-admin ──────────────────────────────────────
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.es_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── Helpers carrito (sesión servidor) ────────────────────────
def get_carrito():      return session.get('carrito', {})
def save_carrito(c):    session['carrito'] = c; session.modified = True

# ══════════════════════════════════════════════════════════════
# RUTAS PÚBLICAS
# ══════════════════════════════════════════════════════════════
@app.route('/')
def index():
    productos = Producto.query.filter(
        Producto.imagen_datos != None
    ).limit(8).all()
    return render_template('index.html', productos=productos)
@app.route('/catalogo')
def catalogo():
    marca_id = request.args.get('marca', type=int)
    busqueda = request.args.get('q', '').strip()
    productos = svc_prod.obtener_todos(marca_id=marca_id, busqueda=busqueda or None)
    marcas    = svc_emp.obtener_todas()
    return render_template('catalogo.html', productos=productos,
                           marcas=marcas, marca_sel=marca_id, busqueda=busqueda)

@app.route('/producto/<int:id_producto>/imagen')
def imagen_producto(id_producto):
    p = svc_prod.obtener_por_id(id_producto)
    if not p.imagen_datos:
        abort(404)
    return Response(p.imagen_datos, mimetype=p.imagen_tipo or 'image/jpeg')

@app.route('/producto/<int:id_producto>')
def detalle_producto(id_producto):
    producto = svc_prod.obtener_por_id(id_producto)
    return render_template('detalle_producto.html',
                           producto=producto)

# ══════════════════════════════════════════════════════════════
# AUTENTICACIÓN
# ══════════════════════════════════════════════════════════════
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard') if current_user.es_admin()
                        else url_for('perfil'))
    form     = LoginForm()
    reg_form = RegistroForm()
    if form.validate_on_submit():
        user = svc_usr.obtener_por_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'¡Bienvenida, {user.nombre}! 💄', 'success')
            return redirect(url_for('admin_dashboard') if user.es_admin()
                            else url_for('index'))
        flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html', form=form, reg_form=reg_form)

@app.route('/registro', methods=['POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        user, error = svc_usr.registrar_usuario(form)
        if error:
            flash(error, 'error')
            return redirect(url_for('login') + '?tab=registro')
        login_user(user)
        flash('¡Cuenta creada! Bienvenida a Brillo-Boom 🌸', 'success')
        return redirect(url_for('perfil'))
    for errs in form.errors.values():
        for e in errs: flash(e, 'error')
    return redirect(url_for('login') + '?tab=registro')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))

# OAuth social (placeholders — conectar con Flask-Dance en producción)
@app.route('/auth/google')
def auth_google():
    flash('Inicio con Google próximamente disponible.', 'info')
    return redirect(url_for('login'))

@app.route('/auth/facebook')
def auth_facebook():
    flash('Inicio con Facebook próximamente disponible.', 'info')
    return redirect(url_for('login'))

@app.route('/auth/instagram')
def auth_instagram():
    flash('Inicio con Instagram próximamente disponible.', 'info')
    return redirect(url_for('login'))

@app.route('/auth/tiktok')
def auth_tiktok():
    flash('Inicio con TikTok próximamente disponible.', 'info')
    return redirect(url_for('login'))

@app.route('/auth/telefono', methods=['POST'])
def auth_telefono():
    tel  = request.form.get('telefono', '').strip()
    user = svc_usr.obtener_por_telefono(tel)
    if user:
        login_user(user)
        flash(f'¡Bienvenida, {user.nombre}!', 'success')
        return redirect(url_for('admin_dashboard') if user.es_admin() else url_for('perfil'))
    flash('Número de teléfono no registrado.', 'error')
    return redirect(url_for('login'))

# ══════════════════════════════════════════════════════════════
# USUARIO — perfil y carrito
# ══════════════════════════════════════════════════════════════
@app.route('/perfil')
@login_required
def perfil():
    if current_user.es_admin():
        return redirect(url_for('admin_dashboard'))
    pedidos = svc_ped.obtener_por_usuario(current_user.id_usuario)
    return render_template('usuario/perfil.html', pedidos=pedidos)

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if current_user.es_admin():
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        current_user.nombre    = request.form.get('nombre', current_user.nombre)
        current_user.telefono  = request.form.get('telefono', current_user.telefono)
        current_user.direccion = request.form.get('direccion', current_user.direccion)
        current_user.foto_url  = request.form.get('foto_url', current_user.foto_url)
        db.session.commit()
        flash('Perfil actualizado correctamente. ✅', 'success')
        return redirect(url_for('perfil'))
    return render_template('usuario/editar_perfil.html')

@app.route('/carrito')
@login_required
def carrito():
    if current_user.es_admin():
        return redirect(url_for('admin_dashboard'))
    carrito = get_carrito()
    items, total = [], 0
    for id_p, qty in carrito.items():
        p = Producto.query.get(int(id_p))
        if p:
            items.append({'producto': p, 'cantidad': qty, 'id_prod': id_p})
            total += p.precio * qty
    return render_template('usuario/carrito.html', items=items, total=total)

@app.route('/carrito/agregar', methods=['POST'])
@login_required
def agregar_carrito():
    data = request.get_json(silent=True) or {}
    id_p = str(data.get('id_producto', ''))
    qty  = max(1, int(data.get('cantidad', 1)))
    if not id_p:
        return jsonify({'ok': False, 'msg': 'Producto inválido'}), 400
    p = Producto.query.get(int(id_p))
    if not p or p.agotado():
        return jsonify({'ok': False, 'msg': 'Producto no disponible'}), 400
    c = get_carrito()
    c[id_p] = c.get(id_p, 0) + qty
    save_carrito(c)
    return jsonify({'ok': True, 'total_items': sum(c.values()), 'nombre': p.nombre})

@app.route('/carrito/actualizar', methods=['POST'])
@login_required
def actualizar_carrito():
    id_p = str(request.form.get('id_producto', ''))
    p = Producto.query.get(int(id_p)) if id_p.isdigit() else None
    if not p:
        flash('Producto inválido.', 'error')
        return redirect(url_for('carrito'))
    try:
        qty = int(request.form.get('cantidad', 1))
    except ValueError:
        qty = 1
    qty = max(1, min(qty, p.stock))
    c = get_carrito()
    c[id_p] = qty
    save_carrito(c)
    flash('Cantidad actualizada. ✅', 'success')
    return redirect(url_for('carrito'))

@app.route('/carrito/eliminar/<id_prod>')
@login_required
def eliminar_carrito(id_prod):
    c = get_carrito(); c.pop(str(id_prod), None); save_carrito(c)
    flash('Producto eliminado del carrito.', 'info')
    return redirect(url_for('carrito'))

@app.route('/carrito/vaciar')
@login_required
def vaciar_carrito():
    save_carrito({})
    flash('Carrito vaciado.', 'info')
    return redirect(url_for('carrito'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.es_admin():
        return redirect(url_for('admin_dashboard'))
    carrito = get_carrito()
    if not carrito:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito'))
    items, total = [], 0
    for id_p, qty in carrito.items():
        p = Producto.query.get(int(id_p))
        if p:
            items.append({'producto': p, 'cantidad': qty})
            total += p.precio * qty
    medios = svc_ped.obtener_medios()
    if request.method == 'POST':
        pedidos, error = svc_ped.crear_desde_carrito(current_user.id_usuario, carrito)
        if error:
            flash(error, 'error')
            return redirect(url_for('checkout'))
        save_carrito({})
        flash('¡Pedido confirmado! 🎉 Gracias por tu compra.', 'success')
        return redirect(url_for('perfil'))
    return render_template('usuario/carrito.html',
                           items=items, total=total,
                           medios=medios, modo_checkout=True)

# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
@app.route('/admin/reportes/usuarios')
@login_required
def reporte_usuarios():
    if not current_user.es_admin():
        abort(403)
    usuarios = Usuario.query.all()
    pdf = svc_rep.generar_reporte_usuarios(usuarios)
    return Response(pdf, mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename="Reporte_Usuarios.pdf"'})


@app.route('/admin/reportes/productos')
@login_required
def reporte_productos():
    if not current_user.es_admin():
        abort(403)
    productos = Producto.query.all()
    pdf = svc_rep.generar_reporte_productos(productos)
    return Response(pdf, mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename="Reporte_Productos.pdf"'})

@app.route('/admin/reportes/productos/excel')
@login_required
def reporte_productos_excel():
    if not current_user.es_admin():
        abort(403)
    productos = Producto.query.all()
    excel_bytes = svc_rep.generar_reporte_productos_excel(productos)
    return Response(excel_bytes,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename="Reporte_Productos.xlsx"'})

@app.route('/admin/reportes/pedidos')
@login_required
def reporte_pedidos():
    if not current_user.es_admin():
        abort(403)
    pedidos = Pedido.query.all()
    pdf = svc_rep.generar_reporte_pedidos(pedidos)
    return Response(pdf, mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename="Reporte_Pedidos.pdf"'})

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = svc_adm.dashboard_stats()
    return render_template('admin/productos.html', stats=stats, vista='dashboard')

@app.route('/admin/productos')
@admin_required
def admin_productos():
    productos = svc_prod.obtener_todos()
    return render_template('admin/productos.html', productos=productos, vista='productos')

@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_producto_nuevo():
    form = ProductoForm()
    form.id_empresa_productos.choices = [
        (e.id_empresa_productos, e.nombre) for e in svc_emp.obtener_todas()
    ]
    if form.validate_on_submit():
        svc_prod.crear(form, form.id_empresa_productos.data)
        flash('Producto creado. ✅', 'success')
        return redirect(url_for('admin_productos'))
    return render_template('admin/form_producto.html', form=form,
                           producto=None, titulo='Nuevo Producto')

@app.route('/admin/productos/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_producto_editar(id):
    prod = svc_prod.obtener_por_id(id)
    form = ProductoForm(obj=prod)
    form.id_empresa_productos.choices = [
        (e.id_empresa_productos, e.nombre) for e in svc_emp.obtener_todas()
    ]
    if form.validate_on_submit():
        svc_prod.actualizar(id, form)
        flash('Producto actualizado. ✅', 'success')
        return redirect(url_for('admin_productos'))
    return render_template('admin/form_producto.html', form=form,
                           producto=prod, titulo='Editar Producto')

@app.route('/admin/productos/<int:id>/eliminar', methods=['POST'])
@admin_required
def admin_producto_eliminar(id):
    svc_prod.eliminar(id)
    flash('Producto eliminado.', 'warning')
    return redirect(url_for('admin_productos'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    usuarios = svc_usr.listar_usuarios()
    return render_template('admin/usuarios.html', usuarios=usuarios, vista='usuarios')

@app.route('/admin/usuarios/<int:id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_usuario(id):
    from models import Pedido, Pago
    usuario = Usuario.query.get_or_404(id)
    if usuario.es_admin():
        flash('No puedes eliminar un administrador.', 'error')
        return redirect(url_for('admin_usuarios'))
    for pedido in usuario.pedidos:
        Pago.query.filter_by(id_pedido=pedido.id_pedido).delete()
    Pedido.query.filter_by(id_usuario=id).delete()
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    pedidos = svc_ped.obtener_todos()
    return render_template('admin/productos.html', pedidos=pedidos, vista='pedidos')

@app.route('/admin/pedidos/<int:id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_pedido(id):
    from models import Pedido, Pago
    pedido = Pedido.query.get_or_404(id)
    Pago.query.filter_by(id_pedido=id).delete()
    db.session.delete(pedido)
    db.session.commit()
    flash('Pedido eliminado correctamente.', 'success')
    return redirect(url_for('admin_pedidos'))

# ══════════════════════════════════════════════════════════════
# ERRORES
# ══════════════════════════════════════════════════════════════
@app.errorhandler(404)
def error_404(e): return render_template('error.html', codigo=404,
    mensaje='Página no encontrada', detalle='La URL que buscas no existe.'), 404

@app.errorhandler(403)
def error_403(e): return render_template('error.html', codigo=403,
    mensaje='Acceso denegado', detalle='No tienes permiso para ver esta sección.'), 403

@app.errorhandler(500)
def error_500(e):
    db.session.rollback()
    return render_template('error.html', codigo=500,
        mensaje='Error del servidor', detalle='Algo salió mal. Intenta de nuevo más tarde.'), 500

# ══════════════════════════════════════════════════════════════
# DATOS INICIALES (seed)
# ══════════════════════════════════════════════════════════════
def seed_data():
    if not Tipo_Usuario.query.first():
        db.session.add_all([Tipo_Usuario(nombre='Administrador'),
                            Tipo_Usuario(nombre='Cliente')])
        db.session.commit()

    if not Usuario.query.filter_by(email='admin@brilloboom.com').first():
        admin = Usuario(nombre='Administrador', email='admin@brilloboom.com',
                        telefono='3001234567', direccion='Sede Principal', id_tipou=1)
        admin.set_password('admin123')
        db.session.add(admin); db.session.commit()

    if not Empresa_Producto.query.first():
        db.session.add_all([Empresa_Producto(nombre='Esika'),
                            Empresa_Producto(nombre="L'bel"),
                            Empresa_Producto(nombre='Cyzone')])
        db.session.commit()

    if not Medio_de_Pago.query.first():
        db.session.add_all([Medio_de_Pago(nombre='Tarjeta de crédito'),
                            Medio_de_Pago(nombre='Tarjeta débito'),
                            Medio_de_Pago(nombre='PSE'),
                            Medio_de_Pago(nombre='Efectivo')])
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
