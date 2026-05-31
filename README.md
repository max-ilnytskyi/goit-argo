# ArgoCD Applications Repository

This repository contains ArgoCD application manifests used to deploy services to the EKS cluster.

## Project Structure

```text
goit-argo/
├── namespaces/
│   ├── application/
│   │   ├── nginx.yaml
│   │   └── ns.yaml
│   └── infra-tools/
│       └── ns.yaml
└── README.md
```

## Deployed Application

The `namespaces/application/nginx.yaml` file defines an ArgoCD `Application` resource that deploys nginx from a Helm chart.

The application configuration includes:

* automated synchronization;
* self-healing;
* pruning of removed resources;
* automatic creation of the target namespace;
* `ClusterIP` service exposure.

## Apply the ArgoCD Application

```bash
kubectl apply -f namespaces/application/nginx.yaml
```

The `application` namespace is created automatically by ArgoCD through the `CreateNamespace=true` sync option.

## Verify the Deployment

Check the ArgoCD Application status:

```bash
kubectl get applications -n infra-tools
```

Expected status:

```text
NAME    SYNC STATUS   HEALTH STATUS
nginx   Synced        Healthy
```

Check the deployed nginx pod and service:

```bash
kubectl get pods -n application
kubectl get svc -n application
```

## Access nginx

Forward the nginx service port to the local machine:

```bash
kubectl port-forward svc/nginx -n application 8081:80
```

Open the application in a browser:

```text
http://localhost:8081
```

Alternatively, verify it from another terminal:

```bash
curl http://localhost:8081
```

## Infrastructure Repository

ArgoCD and the EKS infrastructure are managed in the infrastructure repository:

```text
http://github.com/max-ilnytskyi/goit-mlops-5-6/tree/lesson-7
```
