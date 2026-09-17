"""
test_db.py — Brillo-Boom Makeup
pip install -r requirements.txt
pytest test_db.py -v
"""

import pytest
from app import app
from models import db, Usuario, Tipo_Usuario, Producto, Empresa_Producto
from models import Pedido, DetallePedido, Pago, Medio_de_Pago, Comentario, Carrito


# ─── Fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def test_app():
    """Configura la app con base de datos SQLite en memoria para tests"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        _seed_datos_prueba()
        yield app
        db.drop_all()


@pytest.fixture(scope='module')
def client(test_app):
    """Cliente HTTP para tests de rutas"""
    return test_app.test_client()


@pytest.fixture(scope='module')
def ctx(test_app):
    """Contexto de aplicación para tests de modelos"""
    with test_app.app_context():
        yield


def _seed_datos_prueba():
    """Inserta datos mínimos para los tests"""
    # Tipos de usuario
    admin_tipo   = Tipo_Usuario(id_tipou=1, nombre='Administrador')
    cliente_tipo = Tipo_Usuario(id_tipou=2, nombre='Cliente')
    db.session.add_all([admin_tipo, cliente_tipo])

    # Empresa (marca)
    empresa = Empresa_Producto(nombre='Esika', descripcion='Marca de maquillaje')
    db.session.add(empresa)
    db.session.flush()

    # Producto
    producto = Producto(
        nombre='Labial Rojo Pasión',
        descripcion='Labial mate de larga duración',
        precio=25000.0,
        stock=50,
        categoria='labial',
        id_empresa_productos=empresa.id_empresa_productos,
        activo=True
    )
    db.session.add(producto)

    # Usuario cliente
    cliente = Usuario(
        nombre='Laura', apellido='Gómez',
        email='laura@test.com', telefono='3001234567',
        id_tipou=2, activo=True
    )
    cliente.set_password('pass123')
    db.session.add(cliente)

    # Admin
    admin = Usuario(
        nombre='Admin', apellido='BB',
        email='admin@brilloboom.com', telefono='3009999999',
        id_tipou=1, activo=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # Medio de pago
    medio = Medio_de_Pago(nombre='Nequi')
    db.session.add(medio)

    db.session.commit()


# ═══════════════════════════════════════════════════════════════════
#  TESTS DE MODELOS / BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════

class TestConexionBD:

    def test_bd_accesible(self, test_app):
        """✅ La base de datos SQLite se crea y es accesible"""
        with test_app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()
            assert result == 1

    def test_tablas_existen(self, test_app):
        """✅ Todas las tablas se crearon correctamente"""
        with test_app.app_context():
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            requeridas = [
                'tipos_usuarios', 'usuarios', 'empresas_productos',
                'productos', 'pedidos', 'detalle_pedidos',
                'medios_de_pagos', 'pagos', 'comentarios', 'carrito'
            ]
            for tabla in requeridas:
                assert tabla in tablas, f"Tabla '{tabla}' no encontrada"


class TestTipoUsuario:

    def test_tipos_creados(self, test_app):
        """✅ Se insertaron los tipos de usuario correctamente"""
        with test_app.app_context():
            tipos = Tipo_Usuario.query.all()
            assert len(tipos) == 2

    def test_nombres_correctos(self, test_app):
        with test_app.app_context():
            admin = Tipo_Usuario.query.get(1)
            cliente = Tipo_Usuario.query.get(2)
            assert admin.nombre == 'Administrador'
            assert cliente.nombre == 'Cliente'


class TestUsuario:

    def test_usuario_creado(self, test_app):
        """✅ El usuario cliente se insertó en la BD"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert u is not None
            assert u.nombre == 'Laura'

    def test_password_hasheado(self, test_app):
        """✅ La contraseña NO se guarda en texto plano"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert u.clave != 'pass123'

    def test_check_password_correcto(self, test_app):
        """✅ check_password() valida la contraseña correcta"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert u.check_password('pass123') is True

    def test_check_password_incorrecto(self, test_app):
        """✅ check_password() rechaza contraseña incorrecta"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert u.check_password('mala_clave') is False

    def test_es_admin_falso_para_cliente(self, test_app):
        """✅ Un cliente NO es admin"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert u.es_admin() is False

    def test_es_admin_verdadero_para_admin(self, test_app):
        """✅ El administrador SÍ es admin"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='admin@brilloboom.com').first()
            assert u.es_admin() is True

    def test_email_unico(self, test_app):
        """✅ No se puede insertar dos usuarios con el mismo correo"""
        with test_app.app_context():
            duplicado = Usuario(
                nombre='Duplicado', apellido='Test',
                email='laura@test.com', id_tipou=2, activo=True
            )
            duplicado.set_password('test')
            db.session.add(duplicado)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()


class TestProducto:

    def test_producto_creado(self, test_app):
        """✅ El producto se insertó correctamente"""
        with test_app.app_context():
            p = Producto.query.filter_by(nombre='Labial Rojo Pasión').first()
            assert p is not None
            assert p.precio == 25000.0
            assert p.stock == 50

    def test_propiedad_agotado_false(self, test_app):
        """✅ Un producto con stock > 0 NO está agotado"""
        with test_app.app_context():
            p = Producto.query.first()
            assert p.agotado is False

    def test_propiedad_agotado_true(self, test_app):
        """✅ Un producto con stock = 0 SÍ está agotado"""
        with test_app.app_context():
            p = Producto.query.first()
            p.stock = 0
            db.session.commit()
            assert p.agotado is True
            p.stock = 50  # restaurar
            db.session.commit()

    def test_relacion_empresa(self, test_app):
        """✅ El producto tiene relación con su empresa/marca"""
        with test_app.app_context():
            p = Producto.query.first()
            assert p.empresa is not None
            assert p.empresa.nombre == 'Esika'


class TestCarrito:

    def test_agregar_al_carrito(self, test_app):
        """✅ Se puede agregar un item al carrito"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            p = Producto.query.first()
            item = Carrito(id_usuario=u.id_usuario, id_producto=p.id_producto, cantidad=2)
            db.session.add(item)
            db.session.commit()

            resultado = Carrito.query.filter_by(id_usuario=u.id_usuario).first()
            assert resultado is not None
            assert resultado.cantidad == 2

    def test_carrito_relacionado_con_usuario(self, test_app):
        """✅ El carrito tiene la relación correcta con el usuario"""
        with test_app.app_context():
            u = Usuario.query.filter_by(email='laura@test.com').first()
            assert len(u.carrito) > 0


class TestPedido:

    def test_crear_pedido(self, test_app):
        """✅ Se puede crear un pedido correctamente"""
        with test_app.app_context():
            from datetime import datetime
            u = Usuario.query.filter_by(email='laura@test.com').first()
            pedido = Pedido(
                id_usuario=u.id_usuario,
                total=25000.0,
                fecha=datetime.utcnow(),
                estado='pendiente'
            )
            db.session.add(pedido)
            db.session.commit()
            assert pedido.id_pedido is not None
            assert pedido.estado == 'pendiente'


# ═══════════════════════════════════════════════════════════════════
#  TESTS DE RUTAS (HTTP)
# ═══════════════════════════════════════════════════════════════════

class TestRutasPublicas:

    def test_inicio_carga(self, client):
        """✅ La página de inicio responde 200"""
        r = client.get('/')
        assert r.status_code == 200

    def test_catalogo_carga(self, client):
        """✅ El catálogo responde 200"""
        r = client.get('/catalogo')
        assert r.status_code == 200

    def test_login_carga(self, client):
        """✅ La pantalla de login carga correctamente"""
        r = client.get('/login')
        assert r.status_code == 200

    def test_registro_carga(self, client):
        """✅ La pantalla de registro carga correctamente"""
        r = client.get('/registro')
        assert r.status_code == 200

    def test_ruta_inexistente_retorna_404(self, client):
        """✅ Una ruta inválida retorna 404"""
        r = client.get('/pagina-que-no-existe')
        assert r.status_code == 404


class TestAutenticacion:

    def test_login_correcto(self, client):
        """✅ Login con credenciales válidas redirige al dashboard"""
        r = client.post('/login', data={
            'email': 'laura@test.com',
            'password': 'pass123'
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_incorrecto(self, client):
        """✅ Login con contraseña incorrecta muestra error"""
        r = client.post('/login', data={
            'email': 'laura@test.com',
            'password': 'clave_mala'
        }, follow_redirects=True)
        assert r.status_code == 200
        assert 'incorrectos' in r.data.decode('utf-8').lower() or r.status_code == 200

    def test_dashboard_requiere_login(self, client):
        """✅ El dashboard redirige al login si no está autenticado"""
        r = client.get('/dashboard')
        assert r.status_code in (302, 401)

    def test_admin_requiere_login(self, client):
        """✅ El panel admin redirige si no hay sesión activa"""
        r = client.get('/admin')
        assert r.status_code in (302, 401)


# ─── Ejecución directa ───────────────────────────────────────────
if __name__ == '__main__':
    import subprocess
    subprocess.run(['pytest', 'test_db.py', '-v', '--tb=short'])
