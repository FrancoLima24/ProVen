from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, DateField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])
    precio_compra = FloatField('Precio de Compra', validators=[DataRequired()])
    precio_venta = FloatField('Precio de Venta', validators=[DataRequired()])
    submit = SubmitField('Agregar Producto')

class StockForm(FlaskForm):
    producto = SelectField('Producto', coerce=int, validators=[DataRequired()])
    fecha_ingreso = DateField('Fecha de Ingreso', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_vencimiento = DateField('Fecha de Vencimiento', format='%Y-%m-%d', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Agregar al Stock')


class VentaForm(FlaskForm):
    producto = SelectField('Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad a vender', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Venta')