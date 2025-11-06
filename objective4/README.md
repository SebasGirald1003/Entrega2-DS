# Objetivo 4: Implementación de Microservicios Sock-Shop en Amazon EKS con Almacenamiento Persistente EFS

## 📘 Fuente de referencia

> **Guía base utilizada:** “Instalación de AWS EKS con EFS” (documento base del curso/laboratorio).  
> Todos los comandos, configuraciones y resultados descritos a continuación fueron obtenidos siguiendo dicha guía, con adaptaciones y explicaciones adicionales para asegurar el entendimiento del proceso completo de implementación.

---

## 🧱 Descripción General

El propósito de este objetivo es desplegar una aplicación de microservicios (**Sock-Shop**) dentro de un clúster **Amazon EKS**, utilizando **Amazon Elastic File System (EFS)** como sistema de almacenamiento persistente.

El enfoque de este ejercicio es comprobar cómo los datos almacenados en servicios de bases de datos (como `orders-db`) permanecen disponibles incluso después de reinicios o eliminaciones de pods, validando la persistencia a través del montaje de EFS.

---

## ⚙️ Requisitos Previos

Antes de comenzar, se debe contar con los siguientes componentes:

- Clúster **EKS** operativo.
- Herramientas: `awscli`, `kubectl`, `eksctl`, `helm`.
- **Amazon EFS** configurado en la misma VPC del clúster.
- **Security Groups y Subnets** adecuadamente configurados.
- **IAM Roles** con permisos para EKS y EFS.

**Configuración utilizada:**
- **EFS ID:** `fs-037f6fed76344158a`
- **Namespace:** `sock-shop`
- **Modo de acceso:** `ReadWriteMany (RWX)`

---

## ☁️ Configuración del Almacenamiento (EFS + EKS)

### 1. Crear el StorageClass

Archivo `efs-sc.yaml`:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
```

Aplicar:
```bash
kubectl apply -f efs-sc.yaml
```

---

### 2. Crear el PersistentVolume (PV) y PersistentVolumeClaim (PVC)

Archivo `efs-pv-pvc.yaml`:

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
    volumeHandle: fs-037f6fed76344158a
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

Aplicar:
```bash
kubectl apply -f efs-pv-pvc.yaml -n sock-shop
```

Verificar:
```bash
kubectl get pv,pvc -n sock-shop
```

**Resultado esperado:**
```bash
persistentvolume/efs-pv   Bound
persistentvolumeclaim/efs-pvc   Bound
```
Esto confirma la vinculación exitosa entre EFS y el clúster EKS.

---

## 🧩 Despliegue de la Aplicación Sock-Shop

### 1. Crear el Namespace y desplegar los servicios

```bash
kubectl create namespace sock-shop
kubectl apply -f deploy/ -n sock-shop
```

Verificar:
```bash
kubectl get pods -n sock-shop
```

### 2. Exponer el Front-End

```bash
kubectl expose deployment front-end -n sock-shop   --type=LoadBalancer --port=80 --target-port=8079
```

Ver la URL pública:
```bash
kubectl get svc -n sock-shop
```

**Ejemplo de salida:**
```bash
front-end  LoadBalancer  a17ebd47692194dbd9e012af948f49ce-1510623585.us-east-1.elb.amazonaws.com
```

---

## 💾 Montaje del Volumen EFS en el servicio `orders-db`

### Modificación del Deployment

El archivo `orders-db` fue ajustado para montar el EFS como volumen persistente:

```yaml
volumeMounts:
  - name: efs-storage
    mountPath: /data/db

volumes:
  - name: efs-storage
    persistentVolumeClaim:
      claimName: efs-pvc
```

Guardar como `orders-db-fixed.yaml` y aplicar:

```bash
kubectl apply -f orders-db-fixed.yaml
kubectl rollout restart deployment orders-db -n sock-shop
```

Verificar el montaje dentro del pod:
```bash
kubectl exec -it deploy/orders-db -n sock-shop -- df -h
```

**Salida esperada:**
```bash
127.0.0.1:/   8.0E     0  8.0E   0% /data/db
```

---

### Ajuste de Permisos

En caso de errores de escritura en `/data/db`, ejecutar:

```bash
kubectl exec -it deploy/orders-db -n sock-shop -- bash
chmod -R 777 /data/db
exit
```

Y reiniciar el pod:
```bash
kubectl rollout restart deployment orders-db -n sock-shop
```

---

## ✅ Verificación Final

### Estado General
```bash
kubectl get pods -n sock-shop
```
Todos los pods deben mostrarse como **Running**.

### Logs de orders-db
```bash
kubectl logs deploy/orders-db -n sock-shop --tail=20
```

**Salida esperada:**
```json
"msg":"mongod startup complete"
"msg":"Listening on","attr":{"address":"0.0.0.0:27017"}
"msg":"Waiting for connections"
```

---

## 🧾 Conclusiones

- Se desplegó la aplicación Sock-Shop sobre un clúster EKS operativo.  
- Se configuró EFS como sistema de almacenamiento persistente y compartido.  
- Se montó el volumen de EFS en el servicio de base de datos `orders-db`.  
- Se verificó la persistencia de los datos y el correcto funcionamiento del almacenamiento.  

Todos los resultados fueron obtenidos siguiendo la guía original de implementación de EFS con EKS, agregando observaciones y pasos verificados.

---

## 📚 Referencia Técnica

- Documento original: “Instalación AWS EKS EFS” (PDF del laboratorio oficial).  
- Repositorio base de la aplicación: [https://github.com/microservices-demo/microservices-demo](https://github.com/microservices-demo/microservices-demo)  
- Guía de AWS EFS CSI Driver: [https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html](https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html)

