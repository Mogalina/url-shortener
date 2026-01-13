#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

APP_NAME="url-shortener"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$APP_NAME:$IMAGE_TAG"
K8S_DIR="./deploy/k8s"

echo "==> Starting Kubernetes Deployment for $APP_NAME..."

# Prerequisite checks
if ! command -v kubectl &> /dev/null; then
    echo "Error: 'kubectl' is not installed."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Error: 'docker' is not installed."
    exit 1
fi

# Build the Docker Image
echo "==> Building Docker image..."
# Uses the Dockerfile found in deploy/docker/Dockerfile
docker build -t $FULL_IMAGE_NAME -f deploy/docker/Dockerfile .

# Load Image into local cluster
if command -v minikube &> /dev/null && minikube status | grep -q "Running"; then
    echo "Detected Minikube. Loading image..."
    minikube image load $FULL_IMAGE_NAME
elif command -v kind &> /dev/null && kind get clusters | grep -q "kind"; then
    echo "Detected Kind. Loading image..."
    kind load docker-image $FULL_IMAGE_NAME
else
    echo "No local Minikube or Kind cluster detected active."
    echo "Ensure your Kubernetes cluster can pull '$FULL_IMAGE_NAME'."
    echo "If using Docker Desktop, the local image is already available."
fi

# Apply Kubernetes configurations
if [ -d "$K8S_DIR" ]; then
    echo "==> Applying configurations from $K8S_DIR..."
    kubectl apply -f $K8S_DIR
else
    echo "Error: Directory $K8S_DIR not found."
    echo "Please save the YAML files from the previous step into 'deploy/k8s/'."
    exit 1
fi

# Wait for rollout
echo "==> Waiting for API deployment to be ready..."
kubectl rollout status deployment/api --timeout=60s
kubectl rollout status deployment/redis --timeout=60s
kubectl rollout status statefulset/cassandra --timeout=120s

# Port forwarding
echo ""
echo "Deployment complete!"
echo "The service is running inside the cluster."
echo "Opening port forward to localhost:8000..."
echo ""

# Forward port 8000 from the 'api' service to localhost
kubectl port-forward svc/api 8000:80
