# Objetivo 3: Despliegue en Clúster Kubernetes (EKS)

En este objetivo se evolucionó la aplicación **BookStore Monolítica** para ser desplegada dentro de un **clúster Kubernetes (EKS)** en AWS.  
El propósito fue trasladar la arquitectura de máquinas virtuales hacia un entorno **contenedorizado, escalable y gestionado**, manteniendo la integración con servicios externos de **RDS (base de datos)** y **EFS (almacenamiento compartido)**.

---

## 1. Arquitectura General

La infraestructura implementada en AWS incluye los siguientes componentes:

| Servicio | Descripción |
|-----------|--------------|
| **Amazon EKS** | Clúster Kubernetes administrado para el despliegue de BookStore |
| **Amazon RDS (Aurora MySQL)** | Base de datos gestionada y replicada |
| **Amazon EFS** | Almacenamiento de archivos compartido entre pods |
| **Elastic Load Balancer (ALB)** | Balanceador de carga para exponer el servicio Flask |
| **AWS IAM** | Roles y políticas para acceso controlado desde los nodos del clúster |

El objetivo fue reproducir el entorno de producción del **Objetivo 2**, pero gestionado dentro de Kubernetes.

---

## 2. Configuración del Clúster Kubernetes

### 2.1 Creación del clúster EKS

El clúster se creó mediante el servicio EKS de AWS:

- **Nodos:** t3.medium (Capaces de mantener de 10 a 15 pods estables) 
- **Versión de Kubernetes:** 1.33  
- **Autoscaling habilitado:** Sí
- **Roles IAM:** Permisos configurados para acceso a EFS y RDS desde los nodos del clúster.

---

## 3. Contenedorización de la Aplicación

El Dockerfile fue ajustado para permitir la ejecución de la aplicación Flask en contenedor, las variables de entorno para conectarse a RDS se encuentran en .env:

```dockerfile
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
```

Se construyó la imagen y se subió a **DockerHub para hacer uso de esta en K8S**:

---

## 4. Integración con RDS

- La aplicación se conectó al mismo **RDS Aurora MySQL** creado en el **Objetivo 2**.  
- Se configuró la cadena de conexión en las variables de entorno del **Deployment** de Kubernetes entre un ConfigMap y un Secret:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flask-config
data:
  DB_HOST: bookstore-db.cpakfgfvyj3a.us-east-1.rds.amazonaws.com
  DB_NAME: bookstore
  DB_USER: admin
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: flask-secrets
type: Opaque
stringData:
  DB_PASSWORD: "password"
  SECRET_KEY: "key"
```

---

## 5. Montaje de EFS

Se integró el almacenamiento EFS mediante el **EFS CSI Driver** y Se vinculo este mediante la ID del EFS de AWS

El **Persistent Volume (PV)** y **Persistent Volume Claim (PVC)** se configuraron así:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: flask-efs-pv
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: efs-sc
  csi:
    driver: efs.csi.aws.com
    volumeHandle: fs-0f09039c7f9c218b6.efs.us-east-1.amazonaws.com
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: flask-efs-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 5Gi
```

---

## 6. Despliegue de la Aplicación

El manifiesto principal (`deployment-flask.yaml`) contiene el **Deployment** y **Service** en ClusterIP para la comunicación interna con el Servicio Nginx que contiene (`deployment-nginx.yaml`) para exponer la aplicación a través del **ELB**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flaskapp
  labels:
    app: flaskapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flaskapp
  template:
    metadata:
      labels:
        app: flaskapp
    spec:
      containers:
      - name: flaskapp
        image: sgirald2019/entrega2-ds:latest
        ports:
        - containerPort: 5000
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: flask-config
              key: DB_HOST
        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: flask-config
              key: DB_NAME
        - name: DB_USER
          valueFrom:
            configMapKeyRef:
              name: flask-config
              key: DB_USER
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: flask-secrets
              key: DB_PASSWORD
        - name: FLASK_ENV
          value: production
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: flask-secrets
              key: SECRET_KEY
        volumeMounts:
        - name: flask-storage
          mountPath: /app/uploads
      volumes:
      - name: flask-storage
        persistentVolumeClaim:
          claimName: flask-efs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: flaskapp-service
  labels:
    app: flaskapp
spec:
  type: ClusterIP
  ports:
  - port: 5000
    targetPort: 5000
  selector:
    app: flaskapp
```
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-conf
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
      volumes:
      - name: nginx-conf
        configMap:
          name: nginx-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    events {}
    http {
      server {
        listen 80;
        location / {
          proxy_pass http://flaskapp-service:5000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
        }
      }
    }
```

---

## 7. Certificación SSL y Dominio

Debido a problemas con los permisos de AWS y la AMI no se pudo realizar la certificación SSL del objetivo, se comparte a continuación la dirección del ELB que contiene la aplicación.

URL final: http://a78a7fd1ac37a4734bd20136f8df93a6-1007279366.us-east-1.elb.amazonaws.com

---

## 8. Validaciones finales

| Validación | Resultado |
|-------------|------------|
| Aplicación desplegada en EKS | ✅ |
| Conexión RDS funcional | ✅ |
| Almacenamiento EFS compartido | ✅ |
| Escalamiento horizontal (HPA) | ✅ |

---

## 9. Conclusiones

- Se logró migrar la aplicación monolítica a un entorno **Kubernetes administrado (EKS)**.  
- Se mantuvo la integración con **RDS** y **EFS**, replicando la funcionalidad del entorno anterior.  
- El uso de **ELB** permitió balanceo de carga y exposición pública segura.  
- La arquitectura resultante está lista para evolucionar a microservicios (Objetivo 4).

---
