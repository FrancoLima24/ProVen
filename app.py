from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Importa las rutas después de configurar la app
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Asegúrate de que las tablas se creen correctamente en la base de datos
    app.run(debug=True)

