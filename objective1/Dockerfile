# Usa una imagen oficial ligera de Python
FROM python:3.10-slim

# Evita buffering en logs (útil en Docker)
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Copia requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instala dependencias de Python (sin gunicorn)
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente
COPY . .

# Expone el puerto donde correrá Flask
EXPOSE 5000

# Define variables de entorno de Flask
# (ajusta el nombre del archivo principal, por ejemplo main.py, app.py, etc.)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Comando por defecto: ejecutar Flask directamente
CMD ["flask", "run"]


