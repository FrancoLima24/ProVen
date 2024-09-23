from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from models import Producto, Stock, Venta, PrecioHistorico, Promocion
from forms import ProductoForm, StockForm, VentaForm
from datetime import datetime, date
from sqlalchemy import func

@app.route('/')
def index():
    productos = Producto.query.all()

    # Obtener ventas con la información necesaria
    ventas = Venta.query.join(Producto).all()

    # Obtener stock disponible con la información necesaria
    stock = Stock.query.join(Producto).filter(Stock.vendido == False).all()

    # Calcular el stock disponible por producto
    stock_disponible_por_producto = {
        producto.id: Stock.query.filter_by(id_producto=producto.id, vendido=False).count() 
        for producto in productos
    }

    # Consultar las ventas agrupadas por mes
    result = db.session.execute(
        db.text("""
            SELECT FORMAT([Venta].fecha_venta, 'yyyy-MM') AS mes, COUNT([Venta].id) AS ventas
            FROM [Venta]
            GROUP BY FORMAT([Venta].fecha_venta, 'yyyy-MM')
        """)
    )
    
    # Convertir resultados a listas de tuplas
    ventas_mensuales = [(row[0], row[1]) for row in result]

    # Calcular ventas totales y stock total
    ventas_totales = Venta.query.count()
    total_stock = Stock.query.filter_by(vendido=False).count()

    # Obtener la fecha actual
    hoy = date.today()

    # Alertas de productos próximos a vencer
    productos_por_vencer = Stock.query.filter(
        Stock.fecha_vencimiento <= hoy, 
        Stock.vendido == False
    ).all()

    # Revisar si hay promociones activas
    promociones_activas = Promocion.query.filter(
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).all()

    # Control de acceso por roles
    usuario_rol = session.get('usuario_rol', 'empleado')  # Ejemplo de cómo manejar los roles en sesión
    puede_ver_detalles = usuario_rol == 'encargado'  # Solo los encargados ven ciertos detalles

    return render_template(
        'index.html', 
        productos=productos, 
        stock_disponible_por_producto=stock_disponible_por_producto,
        ventas_totales=ventas_totales, 
        total_stock=total_stock, 
        ventas_mensuales=ventas_mensuales,  
        hoy=hoy,  
        productos_por_vencer=productos_por_vencer,  # Pasar la lista de productos por vencer
        promociones_activas=promociones_activas,  # Pasar promociones activas al template
        puede_ver_detalles=puede_ver_detalles,  # Control de acceso por roles
        ventas=ventas,  # Agregar ventas al template
        stock=stock  # Agregar stock al template
    )

# Ruta: Agregar Producto
@app.route('/add_product', methods=['GET', 'POST'])
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

# Ruta: Agregar Stock
@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    form = StockForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    # Obtener el stock existente para mostrarlo en la plantilla
    stock_items = Stock.query.filter_by(vendido=False).all()

    if form.validate_on_submit():
        try:
            producto_id = form.producto.data
            fecha_ingreso = form.fecha_ingreso.data
            fecha_vencimiento = form.fecha_vencimiento.data
            cantidad = form.cantidad.data

            # Agregar n unidades de stock
            for _ in range(cantidad):
                nuevo_stock = Stock(
                    id_producto=producto_id,
                    fecha_ingreso=fecha_ingreso,
                    fecha_vencimiento=fecha_vencimiento
                )
                db.session.add(nuevo_stock)

            db.session.commit()
            flash(f'Se agregaron {cantidad} unidades al stock.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar stock: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('add_stock.html', form=form, stock_items=stock_items)

# Ruta: Registrar una venta
@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    form = VentaForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        producto_id = form.producto.data
        cantidad_a_vender = form.cantidad.data

        try:
            # Obtener el stock disponible no vendido
            stock_disponible = Stock.query.filter_by(id_producto=producto_id, vendido=False).order_by(Stock.fecha_ingreso).all()

            # Verificar si hay suficiente stock
            if len(stock_disponible) < cantidad_a_vender:
                flash('No hay suficiente stock disponible.', 'danger')
                return redirect(url_for('add_sale'))

            # Marcar el stock como vendido y registrar la venta
            for i in range(cantidad_a_vender):
                stock_disponible[i].vendido = True
                nueva_venta = Venta(
                    id_producto=producto_id,
                    id_stock=stock_disponible[i].id
                )
                db.session.add(nueva_venta)

            db.session.commit()
            flash(f'Se registraron {cantidad_a_vender} ventas exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al registrar la venta: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('add_sale.html', form=form)
