# Kubernetes Deployment - Claude RAG Backend

## Architecture

Claude RAG Backend K8s setup showcasing:
- Namespace isolation
- ConfigMap + Secret management
- Rolling update deployment strategy
- Horizontal Pod Autoscaling (HPA)
- Health checks (liveness, readiness, startup)
- Resource limits and requests
- Ingress with nginx controller
- Security context (non-root)

## Quick Start

### Prerequisites
- kubectl configured
- Kubernetes cluster access
- Docker (for building image)

### 1. Build Docker Image
```bash
docker build -t bambusoe02/claude-rag-backend:latest .
docker push bambusoe02/claude-rag-backend:latest
```

### 2. Create Namespace
```bash
kubectl apply -f namespace.yaml
```

### 3. Create Secrets
```bash
kubectl create secret generic claude-rag-secrets \
  --from-literal=ANTHROPIC_API_KEY=your_key \
  --from-literal=OPENAI_API_KEY=your_key \
  -n claude-rag
```

### 4. Deploy All
```bash
kubectl apply -f configmap.yaml -n claude-rag
kubectl apply -f deployment.yaml -n claude-rag
kubectl apply -f service.yaml -n claude-rag
kubectl apply -f hpa.yaml -n claude-rag
kubectl apply -f ingress.yaml -n claude-rag
```

Or deploy everything at once:
```bash
kubectl apply -f . -n claude-rag
```

### 5. Verify
```bash
kubectl get pods -n claude-rag
kubectl get services -n claude-rag
kubectl get ingress -n claude-rag
kubectl get hpa -n claude-rag
```

### 6. Check Logs
```bash
kubectl logs -f deployment/claude-rag-backend -n claude-rag
```

## Scaling

### Manual Scaling
```bash
kubectl scale deployment claude-rag-backend --replicas=3 -n claude-rag
```

### Automatic Scaling
HPA will automatically scale based on CPU (70%) and Memory (80%) utilization:
- Min replicas: 2
- Max replicas: 5

## Monitoring

### Check Pod Status
```bash
kubectl get pods -n claude-rag -o wide
```

### Describe Deployment
```bash
kubectl describe deployment claude-rag-backend -n claude-rag
```

### Check HPA Status
```bash
kubectl get hpa claude-rag-hpa -n claude-rag
kubectl describe hpa claude-rag-hpa -n claude-rag
```

### View Events
```bash
kubectl get events -n claude-rag --sort-by='.lastTimestamp'
```

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name> -n claude-rag
kubectl logs <pod-name> -n claude-rag
```

### Check ConfigMap
```bash
kubectl get configmap claude-rag-config -n claude-rag -o yaml
```

### Check Secrets
```bash
kubectl get secret claude-rag-secrets -n claude-rag
# Note: Secret values are base64 encoded
```

### Port Forward for Testing
```bash
kubectl port-forward service/claude-rag-service 8000:80 -n claude-rag
```

## Features Demonstrated

- **Namespace**: Isolated environment for better resource management
- **ConfigMap**: Non-sensitive configuration management
- **Secret**: Secure API keys management (never commit real secrets!)
- **Deployment**: Rolling updates, replica management, zero-downtime deployments
- **Service**: Internal networking and load balancing
- **Ingress**: External access with SSL/TLS termination
- **HPA**: Auto-scaling based on CPU and Memory metrics
- **Probes**: Comprehensive health monitoring (liveness, readiness, startup)
- **Resource Limits**: CPU and memory constraints for stability
- **Security Context**: Non-root user execution for enhanced security

## Rolling Updates

The deployment uses a `RollingUpdate` strategy:
- `maxSurge: 1` - Allows 1 extra pod during update
- `maxUnavailable: 0` - Ensures zero downtime

To update the image:
```bash
kubectl set image deployment/claude-rag-backend \
  claude-rag-backend=bambusoe02/claude-rag-backend:v1.1.0 \
  -n claude-rag
```

## Cleanup

To remove all resources:
```bash
kubectl delete namespace claude-rag
```

Or delete individual resources:
```bash
kubectl delete -f . -n claude-rag
```

