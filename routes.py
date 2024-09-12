from flask import render_template, redirect, url_for, flash, request
from app import app, db
from models import Producto, Stock, Venta, PrecioHistorico
from forms import ProductoForm, StockForm, VentaForm
from sqlalchemy import func, case
from datetime import datetime

# Ruta para mostrar la página de inicio con productos, ventas y stock
@app.route('/')
def index():
    # Consulta para obtener productos con el stock actual
    productos = db.session.query(
        Producto.id,
        Producto.nombre,
        Producto.categoria,
        Producto.precio_compra,
        Producto.precio_venta,
        func.sum(case((Stock.vendido == False, 1), else_=0)).label('stock_actual'),
        func.min(Stock.fecha_vencimiento).label('fecha_vencimiento')
    ).join(Stock).group_by(
        Producto.id, Producto.nombre, Producto.categoria,
        Producto.precio_compra, Producto.precio_venta
    ).all()

    # Filtros avanzados para productos, si hay parámetros en la consulta
    nombre_filtro = request.args.get('nombre')
    categoria_filtro = request.args.get('categoria')
    min_stock = request.args.get('min_stock')
    max_stock = request.args.get('max_stock')

    # Aplicar filtros a la consulta de productos si se especifican
    if nombre_filtro:
        productos = [p for p in productos if nombre_filtro.lower() in p[1].lower()]
    if categoria_filtro:
        productos = [p for p in productos if categoria_filtro.lower() in p[2].lower()]
    if min_stock:
        productos = [p for p in productos if p[5] >= int(min_stock)]
    if max_stock:
        productos = [p for p in productos if p[5] <= int(max_stock)]

    return render_template('index.html', productos=productos)


# Ruta para agregar una venta
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])

        # Validar que el producto exista y haya stock disponible
        producto = Producto.query.get(id_producto)
        if producto:
            stock_disponible = Stock.query.filter_by(id_producto=id_producto, vendido=False).limit(cantidad).all()

            if len(stock_disponible) >= cantidad:
                # Marcar el stock como vendido y registrar la venta
                for stock in stock_disponible[:cantidad]:
                    stock.vendido = True

                venta = Venta(id_producto=id_producto, fecha_venta=datetime.utcnow())
                db.session.add(venta)
                db.session.commit()
                flash('Venta registrada con éxito', 'success')
            else:
                flash('No hay suficiente stock disponible', 'danger')

        return redirect(url_for('index'))

    productos = Producto.query.all()
    return render_template('add_sale.html', productos=productos)


# Ruta para agregar stock
@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        fecha_vencimiento = request.form['fecha_vencimiento']
        cantidad = int(request.form['cantidad'])

        # Agregar stock para el producto seleccionado
        for _ in range(cantidad):
            nuevo_stock = Stock(
                id_producto=id_producto,
                fecha_vencimiento=datetime.strptime(fecha_vencimiento, '%Y-%m-%d'),
                vendido=False
            )
            db.session.add(nuevo_stock)
        db.session.commit()
        flash('Stock agregado con éxito', 'success')

        return redirect(url_for('index'))

    productos = Producto.query.all()
    return render_template('add_stock.html', productos=productos)


# Ruta para gestionar alertas de productos próximos a vencer
@app.route('/alerts')
def alerts():
    hoy = datetime.utcnow().date()
    alertas = db.session.query(
        Producto.nombre,
        Producto.categoria,
        func.count(Stock.id).label('cantidad'),
        func.min(Stock.fecha_vencimiento).label('fecha_vencimiento')
    ).join(Stock).filter(
        Stock.fecha_vencimiento <= hoy,
        Stock.vendido == False
    ).group_by(
        Producto.id, Producto.nombre, Producto.categoria
    ).all()

    return render_template('alerts.html', alertas=alertas)


# Ruta para ver el resumen de ventas
@app.route('/sales_summary')
def sales_summary():
    resumen = db.session.query(
        Producto.nombre,
        Producto.categoria,
        func.count(Venta.id).label('total_ventas'),
        func.sum(Producto.precio_venta).label('ingreso_total')
    ).join(Venta).group_by(
        Producto.id, Producto.nombre, Producto.categoria
    ).all()

    return render_template('sales_summary.html', resumen=resumen)
