import os

DB_USER = os.getenv("DB_USER", "bookstore_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bookstore_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")  # En producción: IP PRIVADA del EC2-DB
DB_NAME = os.getenv("DB_NAME", "bookstore")

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
