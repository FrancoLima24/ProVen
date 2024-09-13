from flask import render_template, redirect, url_for, flash, request
from app import app, db
from models import Producto, Stock, Venta, PrecioHistorico, Promocion
from forms import ProductoForm, StockForm, VentaForm
from datetime import datetime

@app.route('/')
def index():
    productos = Producto.query.all()  # Obtener todos los productos con sus relaciones
    ventas_totales = db.session.query(db.func.count(Venta.id)).scalar()  # Total de ventas
    total_stock = db.session.query(db.func.count(Stock.id)).filter_by(vendido=False).scalar()  # Stock disponible

    return render_template('index.html', productos=productos, ventas_totales=ventas_totales, total_stock=total_stock)

@app.route('/add_producto', methods=['GET', 'POST'])
def add_product():
    form = ProductoForm()
    if form.validate_on_submit():
        nuevo_producto = Producto(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            precio_compra=form.precio_compra.data,
            precio_venta=form.precio_venta.data
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        # Registrar el precio en el historial
        nuevo_precio = PrecioHistorico(
            id_producto=nuevo_producto.id,
            precio_compra=form.precio_compra.data,
            precio_venta=form.precio_venta.data
        )
        db.session.add(nuevo_precio)
        db.session.commit()

        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('index'))
    return render_template('add_product.html', form=form)

@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    form = StockForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    # Obtener el stock existente para mostrarlo en la plantilla
    stock_items = Stock.query.filter_by(vendido=False).all()

    if form.validate_on_submit():
        producto_id = form.producto.data
        fecha_vencimiento = form.fecha_vencimiento.data
        cantidad = form.cantidad.data

        # Agregar n unidades de stock
        for _ in range(cantidad):
            nuevo_stock = Stock(
                id_producto=producto_id,
                fecha_vencimiento=fecha_vencimiento
            )
            db.session.add(nuevo_stock)

        db.session.commit()
        flash(f'Se agregaron {cantidad} unidades al stock.', 'success')
        return redirect(url_for('index'))

    return render_template('add_stock.html', form=form, stock_items=stock_items)

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    form = VentaForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        producto_id = form.producto.data
        cantidad_a_vender = form.cantidad.data

        # Obtener los productos en stock que no han sido vendidos, ordenados por fecha de ingreso
        stock_disponible = Stock.query.filter_by(id_producto=producto_id, vendido=False).order_by(Stock.fecha_ingreso).all()

        if len(stock_disponible) < cantidad_a_vender:
            flash('No hay suficiente stock disponible.', 'danger')
            return redirect(url_for('add_sale'))

        # Marcar las unidades de stock como vendidas y registrar las ventas
        for i in range(cantidad_a_vender):
            stock_disponible[i].vendido = True
            nueva_venta = Venta(
                id_producto=producto_id,
                id_stock=stock_disponible[i].id
            )
            db.session.add(nueva_venta)

        db.session.commit()
        flash(f'Se registraron {cantidad_a_vender} ventas exitosamente.', 'success')
        return redirect(url_for('index'))

    return render_template('add_sale.html', form=form)
