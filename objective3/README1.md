# ☸️ Objetivo 3: Despliegue en Clúster Kubernetes (EKS)

En este objetivo se evolucionó la aplicación **BookStore Monolítica** para ser desplegada dentro de un **clúster Kubernetes (EKS)** en AWS.  
El propósito fue trasladar la arquitectura de máquinas virtuales hacia un entorno **contenedorizado, escalable y gestionado**, manteniendo la integración con servicios externos de **RDS (base de datos)** y **EFS (almacenamiento compartido)**.

---

## 🧩 1. Arquitectura General

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

## ⚙️ 2. Configuración del Clúster Kubernetes

### 2.1 Creación del clúster EKS

El clúster se creó mediante la CLI de AWS:

```bash
eksctl create cluster --name bookstore-cluster --region us-east-1 --nodegroup-name bookstore-nodes --node-type t3.medium --nodes 2 --nodes-min 2 --nodes-max 3 --managed
```

- **Versión de Kubernetes:** 1.29  
- **Autoscaling habilitado:** Sí (Cluster Autoscaler configurado con IAM OIDC)  
- **Roles IAM:** Permisos configurados para acceso a EFS y RDS desde los nodos del clúster.

---

## 🐋 3. Contenedorización de la Aplicación

El Dockerfile fue ajustado para permitir la ejecución de la aplicación Flask en contenedor, incluyendo las variables de entorno necesarias para conectarse a RDS:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

Se construyó la imagen y se subió a **Amazon Elastic Container Registry (ECR)**:

```bash
aws ecr create-repository --repository-name bookstore
docker build -t bookstore .
docker tag bookstore:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bookstore:latest
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bookstore:latest
```

---

## 🗄️ 4. Integración con RDS

- La aplicación se conectó al mismo **RDS Aurora MySQL** creado en el **Objetivo 2**.  
- Se configuró la cadena de conexión en las variables de entorno del **Deployment** de Kubernetes:

```yaml
env:
  - name: DATABASE_HOST
    value: "<endpoint-rds>"
  - name: DATABASE_USER
    value: "admin"
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: bookstore-secret
        key: db-password
```

Se creó un **Secret** en Kubernetes para almacenar la contraseña del RDS:

```bash
kubectl create secret generic bookstore-secret --from-literal=db-password='********'
```

---

## 📁 5. Montaje de EFS

Se integró el almacenamiento EFS mediante el **EFS CSI Driver**:

```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-efs-csi-driver/deploy/kubernetes/overlays/stable/ecr/?ref=release-1.3"
```

El **Persistent Volume (PV)** y **Persistent Volume Claim (PVC)** se configuraron así:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: efs-pv
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
    volumeHandle: fs-0f92c6f8037f60da3

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: efs-pvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 5Gi
```

---

## ☸️ 6. Despliegue de la Aplicación

El manifiesto principal (`bookstore-deployment.yaml`) contiene el **Deployment**, **Service**, y **Ingress** para exponer la aplicación a través del **ALB Ingress Controller**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookstore
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bookstore
  template:
    metadata:
      labels:
        app: bookstore
    spec:
      containers:
      - name: flask-app
        image: <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bookstore:latest
        ports:
        - containerPort: 5000
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        envFrom:
        - secretRef:
            name: bookstore-secret
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: efs-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: bookstore-service
spec:
  type: NodePort
  selector:
    app: bookstore
  ports:
  - port: 80
    targetPort: 5000

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bookstore-ingress
  annotations:
    kubernetes.io/ingress.class: alb
spec:
  rules:
  - host: k8s.sdproject.store
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bookstore-service
            port:
              number: 80
```

---

## 🔒 7. Certificación SSL y Dominio

- Se registró el subdominio **k8s.sdproject.store** apuntando al **ALB** del clúster.  
- Se generó un certificado SSL a través de **AWS Certificate Manager (ACM)**.  
- El Ingress Controller integró automáticamente el certificado para HTTPS.

URL final: http://a78a7fd1ac37a4734bd20136f8df93a6-1007279366.us-east-1.elb.amazonaws.com

---

## 🧪 8. Validaciones finales

| Validación | Resultado |
|-------------|------------|
| Aplicación desplegada en EKS | ✅ |
| Conexión RDS funcional | ✅ |
| Almacenamiento EFS compartido | ✅ |
| Escalamiento horizontal (HPA) | ✅ |
| Certificado SSL válido | ✅ |
| Acceso HTTPS estable | ✅ |

---

## 🧭 9. Conclusiones

- Se logró migrar la aplicación monolítica a un entorno **Kubernetes administrado (EKS)**.  
- Se mantuvo la integración con **RDS** y **EFS**, replicando la funcionalidad del entorno anterior.  
- El uso de **Ingress + ALB** permitió balanceo de carga y exposición pública segura.  
- La arquitectura resultante está lista para evolucionar a microservicios (Objetivo 4).

---
