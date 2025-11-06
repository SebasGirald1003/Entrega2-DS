# Objetivo 2: Despliegue con auto-escalado en AWS, Base de Datos RDS, Load Balancer y EFS

El objetivo se consistió en desplegar la misma aplicación del anterior objetivo pero ahora con la base de datos en una instancia **RDS**, un **Elastic File System** para guardar archivos y sobre todo lo más importante, con replicación, auto-autoescalamiento con **Auto Scaling Groups** y un **ELB** para el redireccionamiento y distribución de cargas

## 1. Cambios con respecto al anterior objetivo

- Ahora el manifiesto docker-compose.yml es único y contiene las instrucciones para el despliegue de los contenedores correspondientes al **nginx** y la **flaskapp**
- Debido a la creación de la base de datos en RDS, se hicieron los respectivos cambios en el archivo .env
- Se eliminó la configuración SSL (Certificación realizada con ACM de AWS)
- Se añadió un endpoint en la app /health para verificar el estado de las instancias desde el Target Group fácilmente.  
  
Para aplicar estos nuevos cambios se creó una instancia nueva, desde la cual se configuró la base de datos.

## 2. Base de Datos RDS

- Se creo una base de datos Aurora RDS en AWS, ya con el endpoint obtenido se procedió a configurarla desde la instancia antes mencionada con los siguientes comandos:

`mysql -h <endpoint-rds> -u admin -p`  

Se pone la contraseña y luego:  

`CREATE DATABASE bookstore;`

Por último se ingresa a la flaskapp y se crean las tablas con:  
`from extensions import db`
`db.create_all()`


## 3. Creación de EFS

- Se hizo uso del recurso EFS de AWS para la creación del File System y con su dirección `fs-0f92c6f8037f60da3.efs.us-east-1.amazonaws.com` ya era posible hacer el montaje desde las instancias.
- La carpeta dentro de la app queda en la dirección `/uploads/`

## 4. Creación de Imagen AMI y plantilla de lanzamiento

- Ya con la instancia base creada, se procedió a eliminar los procesos que estuvieran activos para dejarla limpia.
- Luego se creo una **Imagen AMI** de esta para usarla como una plantilla de lanzamiento
- Se configuró la plantilla de lanzamiento usando la AMI y siempre el mismo **VPC** y **Security Group** para que no hubiera errores de conexión.
- En las opciones avanzadas de la plantilla de lanzamiento se configuraron las instrucciones del **user-data**

```
#!/bin/bash
apt update -y
apt install -y docker.io docker-compose nfs-common

# Montar EFS
mkdir -p /mnt/efs
mount -t nfs4 fs-0f92c6f8037f60da3.efs.us-east-1.amazonaws.com:/ /mnt/efs

# Montar punto persistente
mkdir -p /mnt/efs/uploads

cd .. # Se hace esto ya que las instancias inician con el usuario root, no usuario ubuntu
cd /home/ubuntu/Entrega2-DS/objective2
docker compose up -d
```

## 5. Creación del TargetGroup

- Se creó un TargetGroup tipo Instancia de nombre **bookstore-tg** con la misma VPC que los anteriores recursos
- También se crearon los chequeos de salud con HTTP puerto 80 al endpoint definido /health

## 6. Creación del Load Balancer

- Se creó el Load Balancer como un Load Balancer de aplicación
- Se asignaron las subredes pertinentes
- Y se configuró el listener HTTP Puerto 80 apuntando al TargetGroup
- Con esto se obtuvo la dirección del LB: `bookstore-lb-d5695ead7c8a3ceb.elb.us-east-1.amazonaws.com`

## 7. Creación de Auto Scaling Group

- Se creó un Auto Scaling Group **bookstore-asg**
- Se asignó la plantilla creada anteriormente con el mismo VPC
- Se habilitaron 3 zonas de disponibilidad (a, b, c)
- Se configuró la capacidad de las instancias así:  
  - Mínimas y Deseadas: 2
  - Máximas: 3
- Se asignó el TargetGroup creado anteriormente.
- Se configuró una politica **Target tracking scaling policy** al 70% de uso de CPU.

## 4. Certificación SSL y Dominio

- Se definió que se iba a usar un subdominio para este objetivo 2.
- Para la certificación de **SSL** se hizo uso del servicio **ACM** de AWS el cual permite certificar dominios y subdominios de manera sencilla y es orientado principalmente al uso de Load Balancers.
- En hostinger creamos el **CNAME** asignado al Load Balancer:  
  - Nombre: autoscale
  - Valor: `bookstore-lb-d5695ead7c8a3ceb.elb.us-east-1.amazonaws.com`
  - TTL: 14400
- Al crear el certificado en ACM se obtuvo la información necesaria para crear el CNAME correspondiente a la certificación:
  - Nombre: _3de77e264b10743d9a49e22846be70a3.autoscale
  - Valor: _b7fa6f8907ad5f93ee397a67a0a4e590.jkddzztszm.acm-validations.aws
  - TTL: 3600  
- También se añadieron algunos registros CAA para facilitar la certificación:
  
![CAA](https://github.com/user-attachments/assets/071a43f1-6aa3-4fd9-b4db-b930407a0bdf)

URL final: https://autoscale.sdproject.store

## 5. Validaciones finales

✅ Aplicación Flask corriendo detrás de NGINX en multiples instancias con auto-scaling.  
✅ Conexión remota estable con la base de datos MySQL en Aurora RDS.  
✅ Acceso HTTPS válido mediante ACM y un Load Balancer de AWS.  
✅ File System (EFS) funcional.  

## 6. Conclusiones

Se cumplió completamente el Objetivo 2.  
Logrando crear una app monolítica con una arquitectura de autoescalamiento, balanceador de carga para controlar tráfico y que a su vez es capaz de almacenar archivos y tolerar fallos.
