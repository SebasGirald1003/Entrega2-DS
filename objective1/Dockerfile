# Usa una imagen oficial ligera de Python
FROM python:3.10-slim

# Evita buffering en logs (útil en Docker)
ENV PYTHONUNBUFFERED=1

# Crea el directorio de la app
WORKDIR /app

# Instala dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Copia requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instala dependencias de Python (incluye gunicorn)
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia el resto del código
COPY . .

# Expone el puerto interno
EXPOSE 5000

# Comando por defecto: ejecutar Gunicorn
# -w 4 -> 4 workers
# -b 0.0.0.0:5000 -> escucha en todas las interfaces
# app:app -> módulo:objeto Flask (ajusta según tu estructura)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

