# Proyecto 2 – Aplicación Escalable: BookStore Monolítica

**Materia:** ST0263 - Tópicos Especiales en Telemática  
**Estudiantes:**  
- Santiago Álvarez Peña - salvarezp4@eafit.edu.co  
- Juan José Vásquez - jjvasquezg@eafit.edu.co  
- Sebastián Giraldo - sgiraldoa7@eafit.edu.co
  
**Profesor:** Edwin Nelson Montoya Munera - emontoya@eafit.edu.co

## VIDEO DEMOSTRATIVO: [Proyecto2SD]()

---

## 1. Descripción general del proyecto

El proyecto **BookStore Monolítica** consiste en una aplicación tipo **E-commerce distribuido** para la venta de libros de segunda mano, donde los usuarios pueden publicar, comprar y vender ejemplares.  
A lo largo del curso, se evolucionó su despliegue desde una arquitectura monolítica básica hasta entornos **escalables y orquestados en Kubernetes**.

El proyecto se desarrolló en **cuatro fases u objetivos**, cada uno con un entorno de despliegue más avanzado:

| Objetivo | Descripción |
|-----------|--------------|
| **1** | Despliegue monolítico en AWS con EC2, NGINX y SSL (Let’s Encrypt). |
| **2** | Escalamiento monolítico con Auto Scaling Groups, Load Balancer, RDS y EFS. |
| **3** | Despliegue en clúster Kubernetes (EKS) con integración RDS y EFS. |
| **4** | Despliegue de una aplicación demo de microservicios en Kubernetes. Fuente: [SocksShop](https://github.com/microservices-demo/microservices-demo) |

---

## 1.1 Aspectos desarrollados

- Despliegue completo de la aplicación en entornos AWS (EC2, RDS, EFS, EKS).  
- Configuración de dominio y certificados SSL (Let’s Encrypt y ACM).  
- Integración continua de servicios: **Flask**, **MySQL**, **NGINX**, **Docker**, **Kubernetes**.  
- Autoescalado y balanceo de carga con **Auto Scaling Groups + ALB**.  
- Persistencia de datos y archivos mediante **Aurora RDS** y **EFS**.  
- Implementación de patrones de despliegue y buenas prácticas de seguridad y disponibilidad.

---

## 1.2 Aspectos no desarrollados

- Faltó implementar Certificación SSL para objetivos 3 y 4 con Kubernetes, pero esto fue debido a la falta de permisos por parte de la AMI en AWS Academy la cuál restringe este tipo de acciones.

---

## 2. Arquitectura y diseño de alto nivel

### Arquitectura general del sistema

El proyecto implementa una arquitectura **monolítica escalable** con las siguientes fases:

```
[Usuarios] → [ALB] → [Nginx + Flask Containers] → [RDS / EFS]
```

- **Capa Web:** NGINX actuando como proxy inverso y punto de entrada HTTP/HTTPS.  
- **Capa Lógica:** Aplicación Flask que gestiona autenticación, catálogo y compras.  
- **Capa de Datos:** Base de datos Aurora MySQL (RDS) y almacenamiento compartido (EFS).  
- **Infraestructura:** AWS EC2 (Objetivo 1 y 2) / Kubernetes EKS (Objetivo 3 y 4).

### Patrones y buenas prácticas aplicadas

- Despliegue reproducible con **Docker y Docker Compose**.  
- Autoescalamiento horizontal con **ASG y Kubernetes HPA**.  
- Desacoplamiento de componentes con servicios administrados (RDS, EFS).  
- Certificados gestionados con **ACM** y **Let’s Encrypt**.  
- Uso de **Infrastructure as Code (IaC)** parcial con `eksctl` y `AWS CLI`.

---

## 3. Ambiente de desarrollo

### Tecnologías principales

| Componente | Versión | Descripción |
|-------------|----------|--------------|
| Python | 3.10 | Lenguaje principal (Flask backend) |
| Flask | 2.3 | Framework web principal |
| Docker / Compose | 24.0 | Contenerización y orquestación básica |
| MySQL | 8.0 | Base de datos relacional |
| NGINX | 1.25 | Proxy inverso y gestor de tráfico |
| AWS CLI / eksctl | latest | Administración de infraestructura AWS |
| Kubernetes | 1.29 | Orquestación de contenedores (EKS) |

### Compilación y ejecución

```bash
# Clonar el repositorio
git clone https://github.com/SebasGirald1003/Entrega2-DS.git
cd Entrega2-DS

# Construir contenedores locales
docker compose up -d --build
```

### Configuración de variables de entorno

| Variable | Descripción | Ejemplo |
|-----------|--------------|----------|
| DATABASE_HOST | Endpoint de la base de datos | bookstore-db.xxxxx.us-east-1.rds.amazonaws.com |
| DATABASE_USER | Usuario de conexión | admin |
| DATABASE_PASSWORD | Contraseña del usuario | ****** |
| SECRET_KEY | Clave de sesión Flask | secretkey123 |
| UPLOAD_FOLDER | Carpeta de almacenamiento de archivos | /mnt/efs/uploads |

### Estructura de directorios

```
Entrega2-DS/
│
├── objective1/
│   ├── controllers/
│   ├── models/
│   ├── templates/
│   ├── .env
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── requirements.txt
│   ├── docker-compose-app.yml
│   ├── docker-compose-mysql.yml
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── ssl.conf
│   └── README.md
│
├── objective2/
│   ├── controllers/
│   ├── models/
│   ├── templates/
│   ├── .env
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── requirements.txt
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── nginx.conf
│   └── README.md
│
├── objective3/
│   ├── controllers/
│   ├── models/
│   ├── templates/
│   ├── k8s/
│   │   └── storage-efs.yaml
│   │   ├── deployment-flask.yaml
│   │   ├── deployment-nginx.yaml
│   │   ├── private-ecr-driver.yaml
│   │   └── configmap.yaml
│   │   └── secrets.yaml
│   │   └── service-loadbalancer.yaml
│   ├── .env
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── nginx.conf
│   └── README.md
│
├── objective4/
│    ├── README.md                
│    └── k8s/
│         ├── efs-sc.yaml           
│         ├── efs-pv-pvc.yaml 
│         ├── orders-db-fixed.yaml 
│         └── namespace.yaml      
└── README_GENERAL.md

```

---

## 4. Ambiente de ejecución (producción)

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| **Infraestructura Base** | AWS EC2 / EKS / TargetGroups | Entornos desplegados en nube |
| **Base de Datos** | Aurora MySQL (RDS) | Persistencia de datos y Alta Disponibilidad |
| **Almacenamiento** | Elastic File System (EFS) | Archivos compartidos |
| **Certificados SSL** | Let’s Encrypt / ACM | Comunicación segura |
| **Escalamiento** | Auto Scaling Groups / HPA | Escalado horizontal |
| **Balanceo de Carga** | ALB | Distribución de tráfico |

### URLs de despliegue

| Entorno | URL |
|----------|------|
| Objetivo 1 | [https://sdproject.store](https://sdproject.store) |
| Objetivo 2 | [https://autoscale.sdproject.store](https://autoscale.sdproject.store) |
| Objetivo 3 | [Objetivo3 sin SSL](http://a78a7fd1ac37a4734bd20136f8df93a6-1007279366.us-east-1.elb.amazonaws.com) |
| Objetivo 4 | [Objetivo4 sin SSL](http://a17ebd47692194dbd9e012af948f49ce-1510623585.us-east-1.elb.amazonaws.com) |

### Ejecución en producción

Cada entorno se despliega automáticamente al iniciar sus servicios, ya sea en Docker, EC2 o Kubernetes.  
Para el entorno EKS:

```bash
kubectl apply -f manifests/
kubectl get pods,svc,ingress
```

---

## 5. Referencias y recursos

- [Repositorio base del curso ST0263](https://github.com/st0263eafit/st0263-252/tree/main/proyecto2)  
- [Documentación Flask](https://flask.palletsprojects.com/)  
- [NGINX Docs](https://docs.nginx.com/)  
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)  
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)  
- [AWS EFS Documentation](https://docs.aws.amazon.com/efs/)  
- [Certbot / Let’s Encrypt](https://certbot.eff.org/)

---

**Autores:** *Santiago Álvarez Peña, Juan José Vásquez, Sebastián Giraldo*  
**Fecha:** Noviembre 2025
