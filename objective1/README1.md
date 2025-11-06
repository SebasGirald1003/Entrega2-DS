# 🧩 Objetivo 1: Despliegue básico en AWS

Este objetivo consistió en desplegar la aplicación **BookStore Monolítica** en dos máquinas virtuales (**EC2**) dentro de **AWS**, separando la lógica de la aplicación y la base de datos.  
Además, se configuró un **dominio propio**, un **proxy inverso con NGINX** y un **certificado SSL** para habilitar tráfico seguro mediante **HTTPS**.

---

## ☁️ 1. Infraestructura en AWS

El despliegue se realizó sobre dos instancias EC2 dentro de la misma **VPC**, utilizando una **subred privada** para la base de datos y una **subred pública** para la aplicación.

| Instancia | Rol | SO | Componentes | Puertos | Dirección |
|------------|-----|----|--------------|----------|-------------|
| **EC2-A** | Aplicación | Ubuntu 22.04 | Docker, Docker Compose, Flask, NGINX, Certbot | 22, 80, 443 | `52.206.55.124` (IP elástica) |
| **EC2-B** | Base de datos | Ubuntu 22.04 | Docker + MySQL 8.0 | 22, 3306 | `172.31.27.147` (IP privada) |

Ambas instancias comparten el mismo **grupo de seguridad** con reglas específicas que permiten la comunicación interna entre servicios.

---

## 🗄️ 2. Servidor de Base de Datos (EC2-B)

La base de datos **MySQL 8.0** fue desplegada en un contenedor Docker utilizando **Docker Compose**.  
Se configuró el parámetro `--bind-address=0.0.0.0` para permitir conexiones desde la aplicación.

📄 **Archivo de despliegue:**  
[📘 docker-compose-mysql.yml](https://github.com/SebasGirald1003/Entrega2-DS/blob/main/objective1/docker-compose-mysql.yml)

📦 **Despliegue:**
```bash
docker compose -f docker-compose-mysql.yml up -d
```

🔐 **Seguridad:**
- Solo la IP privada de **EC2-A** tiene acceso al puerto **3306**.
- Contraseña del usuario MySQL definida por variable de entorno en el contenedor.
- Persistencia de datos en volumen local `/var/lib/mysql`.

---

## ⚙️ 3. Servidor de Aplicación (EC2-A)

El servidor principal ejecuta dos contenedores:
1. **Flask App** — Contenedor que corre la aplicación BookStore.
2. **NGINX** — Proxy inverso que enruta tráfico hacia Flask y gestiona HTTPS.

📦 **Despliegue:**
```bash
docker compose -f docker-compose-app.yml up -d --build
```

🧩 **Características técnicas:**
- Red interna `bookstore_net` compartida con los contenedores.
- Proxy inverso redirigiendo HTTP → HTTPS.
- Certificados SSL montados en `/etc/letsencrypt/live/`.
- Redirección automática de `http://` a `https://`.

---

## 🔒 4. Certificación SSL y Dominio

Se registró el dominio **sdproject.store** en **Hostinger** y se configuraron los registros DNS:

| Tipo | Nombre | Valor |
|------|---------|--------|
| A | @ | 52.206.55.124 |
| A | www | 52.206.55.124 |

📜 **Certificado SSL:**
```bash
sudo certbot certonly --standalone -d sdproject.store -d www.sdproject.store
```

Los certificados se integraron al contenedor **NGINX** y el sitio quedó disponible mediante **HTTPS**:

🔗 **URL final:** [https://sdproject.store](https://sdproject.store)

---

## 🧪 5. Validaciones finales

| Validación | Resultado |
|-------------|------------|
| Conexión Flask ↔ MySQL | ✅ Exitosa (red privada AWS) |
| Certificado SSL activo | ✅ Let’s Encrypt válido |
| Proxy inverso funcional | ✅ Redirección HTTP → HTTPS |
| Acceso externo a dominio | ✅ Disponible en navegador |
| Persistencia de datos | ✅ Verificada tras reinicio de contenedores |

---

## 🧭 6. Conclusiones

- Se logró una **separación efectiva** entre la capa de aplicación y la base de datos en **instancias independientes**.  
- La configuración de **NGINX + Certbot** permitió asegurar las comunicaciones con **HTTPS**.  
- La infraestructura está lista para escalar horizontalmente (Objetivo 2) mediante **autoescalamiento y balanceo de carga (ELB)**.  
- Este entorno cumple con las prácticas recomendadas de despliegue para aplicaciones monolíticas en AWS.

---

## 📚 Referencias

- [Repositorio base del curso](https://github.com/st0263eafit/st0263-252/blob/main/proyecto2/BookStore.zip)
- [Documentación Flask](https://flask.palletsprojects.com/)
- [Documentación NGINX](https://docs.nginx.com/)
- [Guía AWS EC2](https://docs.aws.amazon.com/ec2/)
- [Certbot / Let’s Encrypt](https://certbot.eff.org/)

---