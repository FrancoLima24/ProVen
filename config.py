import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mi_clave_secreta'
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://sa:sql@localhost/VentasPro'
        '?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
