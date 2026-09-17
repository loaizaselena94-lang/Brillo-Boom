# 💄 Brillo-Boom Makeup — Sistema Web Completo

Tienda de maquillaje online con panel de usuario y panel de administración.
Marcas: **Esika · E'bel · Cyzone **

---

## 📁 Estructura del proyecto

```
brillo-boom/
│
├── app.py                  ← Aplicación Flask principal (todas las rutas)
├── models.py               ← Base de datos SQLAlchemy (todas las tablas)
├── forms.py                ← Formularios Flask-WTF con validaciones
├── config.py               ← Configuración: BD, secret key, correo
├── test_db.py              ← Tests automáticos (pytest)
├── requirements.txt        ← Dependencias Python
│
├── servicios/              ← Lógica de negocio separada por módulo
│   ├── usuarios.py
│   ├── admin.py
│   ├── productos.py
│   ├── empresas_productos.py
│   ├── pedidos.py          ← también incluye medios_de_pagos, pagos, tipos_usuarios
│
├── static/
│   ├── css/
│   │   └── style.css       ← Estilos: colores Brillo-Boom + animaciones
│   ├── js/
│   │   └── main.js         ← Lógica frontend: tabs, carrito, validaciones
│   └── images/
│       ├── logo_1.webp     ← Logo principal (brillo-boom makeup)
│       └── logo_2.webp     ← Logo secundario (sello circular)
│
└── templates/
    ├── base.html           ← Template base con navbar y footer
    ├── index.html          ← Página de inicio
    ├── catalogo.html       ← Catálogo con filtros
    ├── detalle_producto.html ← Detalle de producto + reseñas
    ├── login.html          ← Login + Registro con tabs y redes sociales
    ├── error.html          ← Página de error (404, 403, 500)
    ├── usuario/
    │   ├── perfil.html     ← Panel del cliente
    │   └── carrito.html    ← Carrito de compras
    └── admin/
        ├── dashboard.html  ← Dashboard con estadísticas y gráficos
        ├── productos.html  ← Gestión de productos
        ├── usuarios.html   ← Lista de usuarias
        ├── comentarios.html← Moderación de reseñas
        ├── contabilidad.html ← Ventas mensuales con gráfico
        └── form_producto.html ← Crear/editar producto
```

---

## 🗄️ Base de datos — Tablas

| Tabla | Descripción |
|---|---|
| `tipos_usuarios` | Administrador (1) / Cliente (2) |
| `usuarios` | Clientes y admins con contraseña hasheada |
| `empresas_productos` | Marcas: Esika, E'bel, Cyzone |
| `productos` | Catálogo con stock, precio, imagen, categoría |
| `pedidos` | Cabecera del pedido (estado, total, fecha) |
| `detalle_pedidos` | Líneas de cada pedido (producto, cantidad, subtotal) |
| `medios_de_pagos` | Nequi, PSE, Tarjeta, Efectivo... |
| `pagos` | Registro de pagos realizados |

---

## 🚀 Instalación y ejecución

```bash
# 1. Clonar / descomprimir el proyecto
cd brillo-boom

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

Abre tu navegador en: **http://localhost:5000**

---

## 🧪 Ejecutar tests

```bash
pytest test_db.py -v
```

Los tests verifican:
- Conexión a la base de datos
- Creación de todas las tablas
- Hash y verificación de contraseñas
- Relaciones entre modelos
- Rutas HTTP (200, 404, redirecciones)
- Autenticación de usuarios y admins

---

## 👤 Usuarios por defecto (se crean al iniciar)

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@brilloboom.com | admin123 |

*(Los clientes se registran desde la página)*

---

## 🎨 Paleta de colores

| Color | Hex | Uso |
|---|---|---|
| Agua de Rosas | `#FFD6D6` | Fondos suaves, hovers |
| Blanco | `#FFFFFF` | Cards, formularios |
| Carmesí Vívido | `#DC1537` | Botones, títulos, acentos |

**Tipografía:** Poppins (Google Fonts)

---

## 📱 Funcionalidades por rol

### Cliente
- Ver catálogo, filtrar por marca y categoría
- Buscar productos
- Registrarse / Iniciar sesión (correo, Google, Facebook, Instagram, TikTok, teléfono)
- Agregar productos al carrito
- Confirmar pedido
- Ver historial de pedidos
- Dejar reseñas con calificación

### Administrador
- Dashboard con estadísticas (usuarios, productos, ventas del mes)
- Gestión de productos (crear, editar, activar/desactivar)
- Ver lista de usuarias registradas
- Moderar comentarios (mostrar/ocultar)
- Contabilidad mensual con gráfico de barras
- Ver productos agotados
- Ver productos más pedidos
