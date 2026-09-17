# forms.py — Brillo-Boom
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, SelectField,
                     TextAreaField, BooleanField, IntegerField, FloatField)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange

class LoginForm(FlaskForm):
    email    = StringField('Correo electrónico',
                           validators=[DataRequired('El correo es obligatorio.'),
                                       Email('Ingresa un correo válido.')])
    password = PasswordField('Contraseña',
                             validators=[DataRequired('La contraseña es obligatoria.')])
    remember = BooleanField('Recordarme')
    submit   = SubmitField('Iniciar sesión')

class RegistroForm(FlaskForm):
    nombre    = StringField('Nombre completo',
                            validators=[DataRequired(), Length(min=2, max=40)])
    email     = StringField('Correo electrónico',
                            validators=[DataRequired(), Email()])
    telefono  = StringField('Teléfono',
                            validators=[DataRequired(), Length(min=7, max=20)])
    direccion = StringField('Dirección',
                            validators=[DataRequired(), Length(min=5, max=100)])
    password  = PasswordField('Contraseña',
                              validators=[DataRequired(),
                                          Length(min=6, message='Mínimo 6 caracteres.')])
    confirmar = PasswordField('Confirmar contraseña',
                              validators=[DataRequired(),
                                          EqualTo('password', message='Las contraseñas no coinciden.')])
    submit    = SubmitField('Crear cuenta')

class ProductoForm(FlaskForm):
    nombre               = StringField('Nombre del producto',
                                       validators=[DataRequired(), Length(max=40)])
    descripcion          = TextAreaField('Descripción',
                                        validators=[DataRequired(), Length(max=200)])
    precio               = FloatField('Precio (COP)',
                                     validators=[DataRequired(), NumberRange(min=0)])
    stock                = IntegerField('Stock disponible',
                                       validators=[DataRequired(), NumberRange(min=0)])
    imagen               = FileField('Imagen del producto',
                                     validators=[Optional(), FileAllowed(
                                         ['jpg', 'jpeg', 'png', 'webp', 'gif'],
                                         'Solo se permiten imágenes (jpg, png, webp, gif).')])
    id_empresa_productos = SelectField('Marca', coerce=int, validators=[DataRequired()])
    submit               = SubmitField('Guardar producto')
