from flask import Flask, redirect, url_for
from config import Config
from models import db, Usuarios
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Crear la app Flask
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'TORRIKO'

# Inicializar las extensiones
db.init_app(app)
bcrypt = Bcrypt(app)

# Inicializar LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Nombre de la ruta para el login

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# Importar las rutas después de configurar la app
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Asegúrate de que las tablas se creen correctamente en la base de datos
    app.run(debug=True)
