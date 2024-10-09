from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from app import app, db
from models import Producto, Stock, Venta, PrecioHistorico, Promocion, Usuarios, Roles, TotalesNegocio
from forms import ProductoForm, StockForm, VentaForm, LoginForm, RegisterForm
from datetime import datetime, date

 

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(nombre=form.nombre.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)  # Inicia sesión del usuario
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')  # Mensaje de error si las credenciales son incorrectas
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Cierra la sesión del usuario
    return redirect(url_for('login'))  # Redirige al login

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        id_rol = request.form.get('id_rol')

        # Verificar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))

        # Verificar que el rol es válido
        rol = Roles.query.filter_by(id=id_rol).first()
        if not rol:
            flash('Rol no válido', 'danger')
            return redirect(url_for('register'))

        # Si es una modificación, buscamos el usuario existente
        usuario_existente = Usuarios.query.filter_by(nombre=nombre).first()
        if usuario_existente:
            usuario_existente.set_password(password)
            usuario_existente.id_rol = rol.id
            flash('Usuario actualizado con éxito', 'success')
        else:
            # Crear nuevo usuario
            nuevo_usuario = Usuarios(nombre=nombre)
            nuevo_usuario.set_password(password)
            nuevo_usuario.id_rol = rol.id
            db.session.add(nuevo_usuario)
            flash('Usuario registrado con éxito', 'success')

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/')
def index():
    if not current_user.is_authenticated:  # Verifica si el usuario no está autenticado
        return redirect(url_for('login'))  # Redirige al login si no está autenticado
    
    # Aquí agregas la lógica para mostrar la información del índice
    productos = Producto.query.all()
    ventas = Venta.query.join(Producto).all()
    stock = Stock.query.join(Producto).filter(Stock.vendido == False).all()

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

    ventas_mensuales = [(row[0], row[1]) for row in result]
    ventas_totales = Venta.query.count()
    total_stock = Stock.query.filter_by(vendido=False).count()
    hoy = date.today()

    productos_por_vencer = Stock.query.filter(
        Stock.fecha_vencimiento <= hoy, 
        Stock.vendido == False
    ).all()

    promociones_activas = Promocion.query.filter(
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).all()

    return render_template(
        'index.html', 
        productos=productos, 
        stock_disponible_por_producto=stock_disponible_por_producto,
        ventas_totales=ventas_totales, 
        total_stock=total_stock, 
        ventas_mensuales=ventas_mensuales,  
        hoy=hoy,  
        productos_por_vencer=productos_por_vencer,  
        promociones_activas=promociones_activas,  
        ventas=ventas,  
        stock=stock  
    )

# Ruta: Agregar Producto
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
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
@login_required
def add_stock():
    form = StockForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    stock_items = Stock.query.filter_by(vendido=False).all()

    if form.validate_on_submit():
        try:
            producto_id = form.producto.data
            fecha_ingreso = form.fecha_ingreso.data
            fecha_vencimiento = form.fecha_vencimiento.data
            cantidad = form.cantidad.data

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
@login_required
def add_sale():
    form = VentaForm()
    form.producto.choices = [(p.id, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        producto_id = form.producto.data
        cantidad_a_vender = form.cantidad.data

        try:
            stock_disponible = Stock.query.filter_by(id_producto=producto_id, vendido=False).order_by(Stock.fecha_ingreso).all()

            if len(stock_disponible) < cantidad_a_vender:
                flash('No hay suficiente stock disponible.', 'danger')
                return redirect(url_for('add_sale'))

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


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    if request.method == 'POST':
        # Obtener los parámetros del formulario
        id_producto = request.form.get('id_producto')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        # Validar que los campos estén completos
        if not id_producto or not fecha_inicio or not fecha_fin:
            flash('Todos los campos son requeridos.')
            return redirect(url_for('reports'))

        # Convertir las fechas a formato de SQL
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha incorrecto.')
            return redirect(url_for('reports'))

        # Llamar al stored procedure con los parámetros
        try:
            # Conexión directa a la base de datos
            engine = db.engine
            with engine.connect() as conn:
                sql = text("""
                    EXEC sp_ReporteVentasPorProductoYFechas :id_producto, :fecha_inicio, :fecha_fin
                """)
                result = conn.execute(sql, {'id_producto': id_producto, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})
                reporte = result.fetchall()
                return render_template('resultado_reporte.html', reporte=reporte)
        except Exception as e:
            flash(f'Error al generar el reporte: {str(e)}')
            return redirect(url_for('reports'))

    return render_template('reports.html')