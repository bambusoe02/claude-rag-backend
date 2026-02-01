#!/bin/bash
# Minikube Setup Script for Claude RAG Backend
# Run this script after installing minikube and kubectl

set -e

echo "═══════════════════════════════════════════════════════════"
echo "PHASE 1: VERIFY PREREQUISITES"
echo "═══════════════════════════════════════════════════════════"

echo "Checking versions..."
minikube version
kubectl version --client
docker --version

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 2: START MINIKUBE CLUSTER"
echo "═══════════════════════════════════════════════════════════"

echo "Starting minikube..."
minikube start --driver=docker --cpus=2 --memory=4096

echo "Verifying cluster..."
minikube status
kubectl cluster-info
kubectl get nodes

echo "Enabling addons..."
minikube addons enable metrics-server
minikube addons enable ingress

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 3: BUILD DOCKER IMAGE"
echo "═══════════════════════════════════════════════════════════"

echo "Setting Docker environment to minikube..."
eval $(minikube -p minikube docker-env)

echo "Building Docker image..."
cd "$(dirname "$0")/.."
docker build -t bambusoe02/claude-rag-backend:latest .

echo "Verifying image..."
docker images | grep claude-rag

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 4: DEPLOY TO KUBERNETES"
echo "═══════════════════════════════════════════════════════════"

echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml
kubectl get namespaces | grep claude-rag

echo "Creating ConfigMap..."
kubectl apply -f k8s/configmap.yaml -n claude-rag
kubectl get configmap -n claude-rag

echo ""
echo "⚠️  IMPORTANT: Create secret manually with your API keys:"
echo "kubectl create secret generic claude-rag-secrets \\"
echo "  --from-literal=ANTHROPIC_API_KEY=your_key_here \\"
echo "  --from-literal=OPENAI_API_KEY=your_key_here \\"
echo "  -n claude-rag"
echo ""
read -p "Press Enter after creating the secret..."

echo "Verifying secret..."
kubectl get secret -n claude-rag

echo "Deploying application..."
kubectl apply -f k8s/deployment.yaml -n claude-rag

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=claude-rag-backend -n claude-rag --timeout=120s

echo "Deploying service..."
kubectl apply -f k8s/service.yaml -n claude-rag
kubectl get service -n claude-rag

echo "Deploying HPA..."
kubectl apply -f k8s/hpa.yaml -n claude-rag
kubectl get hpa -n claude-rag

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PHASE 5: ACCESS APPLICATION"
echo "═══════════════════════════════════════════════════════════"

echo "Starting port-forward in background..."
kubectl port-forward service/claude-rag-service 8000:80 -n claude-rag &
PORT_FORWARD_PID=$!
echo "Port-forward PID: $PORT_FORWARD_PID"
sleep 3

echo "Testing health endpoint..."
curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health

echo ""
echo "✅ Deployment complete!"
echo "Access API docs at: http://localhost:8000/docs"
echo "To stop port-forward: kill $PORT_FORWARD_PID"
echo ""
echo "To view logs: kubectl logs -f deployment/claude-rag-backend -n claude-rag"
echo "To scale: kubectl scale deployment claude-rag-backend --replicas=3 -n claude-rag"

