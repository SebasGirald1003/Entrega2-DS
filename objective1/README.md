# Objetivo 1: Despliegue básico en AWS

El objetivo consistió en desplegar la aplicación **BookStore Monolítica** en **dos máquinas virtuales (EC2)** una para la aplicación y otra para la base de datos en AWS, con un **dominio propio, proxy inverso con NGINX** y **certificado SSL**.  

## 1. Infraestructura en AWS

### EC2-A (Aplicación)
- **Sistema Operativo:** Ubuntu 22.04  
- **Componentes:** Docker, Docker Compose, Flask, NGINX, Certbot  
- **Puertos abiertos:** 22, 80, 443  
- **IP elástica:** `52.206.55.124`

### EC2-B (Base de datos)
- **Sistema Operativo:** Ubuntu 22.04  
- **Componentes:** Docker + MySQL 8.0  
- **Puertos abiertos:** 22, 3306  
- **IP privada:** `172.31.27.147`

Ambas instancias se encuentran en la misma **VPC** y comparten la red interna para permitir la conexión privada entre la aplicación y la base de datos.

## 2. Servidor de Base de Datos (EC2-B)

El servidor MySQL se desplegó mediante **Docker Compose**. Ver [Manifiesto SQL](https://github.com/SebasGirald1003/Entrega2-DS/blob/main/objective1/docker-compose-mysql.yml)  
Se configuró el contenedor para aceptar conexiones externas (`--bind-address=0.0.0.0`).

El grupo de seguridad permite tráfico **TCP 3306** desde la IP privada de EC2-A.  
  
Se lanza con:  
`docker compose -f docker-compose-mysql.yml up -d`

## 3. Servidor de Aplicación (EC2-A)

La instancia de aplicación contiene:  
- Un contenedor Flask que ejecuta la app con flask run.
- Un contenedor NGINX actuando como proxy inverso, manejando HTTP → HTTPS y redirección hacia Flask (puerto interno 5000).
- Certificados Let’s Encrypt obtenidos con Certbot.
- Los manifiestos (Dockerfile, docker-compose-app.yml, nginx.conf, ssl.conf) están incluidos en el repositorio.
    
Se lanza con:  
`docker compose -f docker-compose-app.yml up -d --build`

## 4. Certificación SSL y Dominio

- Se registró el dominio sdproject.store en Hostinger.
- En la Zona DNS, se configuraron los registros A:
- @ → 52.206.55.124
- www → 52.206.55.124

Se generó el certificado SSL con:  
  
```sudo certbot certonly --standalone -d sdproject.store -d www.sdproject.store```
  
Los certificados fueron montados en el contenedor NGINX y la app quedó accesible mediante HTTPS.  

URL final: https://sdproject.store

## 5. Validaciones finales

✅ Aplicación Flask corriendo detrás de NGINX con dominio y SSL activo.  
✅ Conexión remota estable con la base de datos MySQL.  
✅ Acceso HTTPS válido mediante Let’s Encrypt.  
✅ Comunicación entre contenedores en red interna (bookstore_net).  

## 6. Conclusiones

- Se cumplió completamente el Objetivo 1, logrando separar la lógica de aplicación y base de datos en diferentes instancias EC2.  
- El sistema quedó configurado con dominio, proxy inverso y certificado SSL, simulando un entorno de despliegue real.  
- Este entorno servirá como base para el Objetivo 2, donde se implementará el autoescalado y balanceo de carga.

## Referencias

- [Repositorio base del curso](https://github.com/st0263eafit/st0263-252/blob/main/proyecto2/BookStore.zip)
- [Documentación Flask](https://flask.palletsprojects.com/)
- [NGINX Docs](https://docs.nginx.com/)
- [AWS EC2 Docs](https://docs.aws.amazon.com/ec2/)
- [Certbot / Let’s Encrypt](https://certbot.eff.org/)

