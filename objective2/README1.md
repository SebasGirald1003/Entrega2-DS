# Objetivo 2: Despliegue con Autoescalado en AWS, RDS, Load Balancer y EFS

El objetivo consistió en desplegar la misma aplicación **BookStore Monolítica** del objetivo anterior, pero ahora integrando **servicios administrados de AWS** para lograr **alta disponibilidad**, **escalabilidad automática** y **resiliencia**.  
Se implementaron los siguientes recursos: **Amazon RDS (Aurora)**, **Elastic File System (EFS)**, **Elastic Load Balancer (ELB)** y **Auto Scaling Groups (ASG)**.

---

## 1. Cambios respecto al objetivo anterior

- Se unificó el manifiesto `docker-compose.yml` para incluir tanto el servicio **NGINX** como **FlaskApp**.  
- Se actualizó el archivo `.env` con las credenciales y endpoint del servicio RDS.  
- Se eliminó el certificado SSL autogenerado (ahora gestionado por **AWS Certificate Manager – ACM**).  
- Se añadió un endpoint `/health` en la aplicación para validación de salud desde el **Target Group**.  
- Se creó una nueva instancia base para preparar la imagen AMI desde la cual se desplegarían las instancias del grupo autoescalable.

---

## 2. Base de Datos RDS (Aurora MySQL)

Se creó una base de datos **Aurora MySQL** administrada por AWS.  
Una vez disponible el **endpoint RDS**, se configuró la conexión desde la instancia base mediante:

```bash
mysql -h <endpoint-rds> -u admin -p
```

Posteriormente se ejecutaron los siguientes comandos:

```sql
CREATE DATABASE bookstore;
```

Y dentro de la aplicación Flask:

```python
from extensions import db
db.create_all()
```

Con esto, las tablas quedaron creadas en RDS y disponibles para todas las instancias del Auto Scaling Group.

---

## 3. Creación del Elastic File System (EFS)

- Se aprovisionó un **EFS** en la misma VPC y subredes que las instancias EC2.  
- Endpoint EFS: `fs-0f92c6f8037f60da3.efs.us-east-1.amazonaws.com`  
- El sistema se montó en `/mnt/efs/uploads`, donde la aplicación almacena archivos compartidos entre instancias.  

Esto garantiza **persistencia y consistencia de archivos** entre réplicas de la aplicación.

---

## 4. Creación de Imagen AMI y Plantilla de Lanzamiento

Después de configurar la instancia base correctamente:

1. Se detuvieron los procesos y contenedores activos.  
2. Se generó una **Imagen AMI** como plantilla base.  
3. Se creó una **Launch Template** utilizando dicha AMI.  
4. Se mantuvieron la misma **VPC** y **Security Groups** para compatibilidad de red.  
5. Se añadió el siguiente **User Data Script** para la configuración automática al iniciar nuevas instancias:

```bash
#!/bin/bash
apt update -y
apt install -y docker.io docker-compose nfs-common

# Montar EFS
mkdir -p /mnt/efs
mount -t nfs4 fs-0f92c6f8037f60da3.efs.us-east-1.amazonaws.com:/ /mnt/efs

# Crear punto persistente
mkdir -p /mnt/efs/uploads

# Iniciar aplicación
cd /home/ubuntu/Entrega2-DS/objective2
docker compose up -d
```

---

## 5. Creación del Target Group

- Nombre: **bookstore-tg**  
- Tipo: **Instance**  
- Protocolo: HTTP (Puerto 80)  
- Health check: Endpoint `/health`  
- VPC: misma que las instancias EC2

El Target Group monitorea las instancias y las asocia dinámicamente al **Load Balancer**.

---

## 6. Creación del Load Balancer

Se configuró un **Application Load Balancer (ALB)** con las siguientes características:

- Subredes: públicas en diferentes zonas de disponibilidad.  
- Listener HTTP puerto 80 → **Target Group: bookstore-tg**.  
- Dominio del balanceador:  
  `bookstore-lb-d5695ead7c8a3ceb.elb.us-east-1.amazonaws.com`  

Este servicio distribuye las peticiones entrantes entre las instancias disponibles en el Auto Scaling Group.

---

## 7. Creación del Auto Scaling Group

- Nombre: **bookstore-asg**  
- Plantilla: Launch Template creada previamente.  
- Zonas de disponibilidad: `us-east-1a`, `us-east-1b`, `us-east-1c`.  
- Capacidad configurada:  
  - **Mínimas:** 2  
  - **Deseadas:** 2  
  - **Máximas:** 3  
- Política de escalamiento: **Target tracking** al **70% de uso de CPU**.  
- Asociado al **Target Group bookstore-tg**.

Con esta configuración, la aplicación se replica automáticamente bajo alta demanda y reduce instancias cuando el uso de CPU baja.

---

## 8. Certificación SSL y Subdominio

Se definió un subdominio para este despliegue: **autoscale.sdproject.store**.

- Se utilizó **AWS Certificate Manager (ACM)** para generar el certificado SSL.  
- En **Hostinger** se configuró un **CNAME** apuntando al Load Balancer:

| Tipo | Nombre | Valor | TTL |
|------|---------|--------|------|
| CNAME | autoscale | `bookstore-lb-d5695ead7c8a3ceb.elb.us-east-1.amazonaws.com` | 14400 |

**CNAME de validación de ACM:**  
- Nombre: `_3de77e264b10743d9a49e22846be70a3.autoscale`  
- Valor: `_b7fa6f8907ad5f93ee397a67a0a4e590.jkddzztszm.acm-validations.aws`  

**Configuración CAA:**  
  
![CAA](https://github.com/user-attachments/assets/071a43f1-6aa3-4fd9-b4db-b930407a0bdf)  

**URL final:** [https://autoscale.sdproject.store](https://autoscale.sdproject.store)

---

## 9. Validaciones finales

| Validación | Resultado |
|-------------|------------|
| FlaskApp detrás de NGINX con autoescalado | ✅ |
| Conexión a base de datos Aurora RDS | ✅ |
| Certificado HTTPS mediante ACM | ✅ |
| Balanceo de carga funcional (ELB) | ✅ |
| EFS compartido entre instancias | ✅ |

---

## 10. Conclusiones

- Se logró una arquitectura **autoescalable, segura y altamente disponible** sobre AWS.  
- La aplicación ahora es capaz de manejar variaciones en la carga y tolerar fallos de manera automática.  
- El uso de **EFS** asegura persistencia compartida y **RDS Aurora** provee una base de datos gestionada y confiable.  
- Este entorno representa una **arquitectura moderna de escalamiento monolítico** antes de la transición hacia microservicios (Objetivo 3).

---
