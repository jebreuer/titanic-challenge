# What is this?

Small coding challenge:

1. create an API which allows interaction with [titanic.db](https://github.com/davidjamesknight/SQLite_databases_for_learning_data_science/blob/main/titanic.db) 
1. make it prod ready

# Known issues

- after fresh setup the api needs a restart before properly connecting to jaeger (this might be a timing issue)

## Development Environment

### Prerequisites for Development

- [Tilt](https://tilt.dev/) (v0.30.0 or later)
- Docker
- Kubernetes cluster (e.g., Docker Desktop with Kubernetes enabled)

### Using Tilt for Development

Tilt automates all the steps needed to build and deploy the application in development mode. It provides hot reloading and real-time feedback for a smoother development experience.

1. Start Tilt:

   ```bash
   tilt up
   ```

2. View the Tilt UI:

Open your web browser and go to http://localhost:10350/

The Tilt UI will show you:

- Build and deployment status
- Live logs from all components
- Resource utilization
- Quick access to service endpoints

### Development Features

- Automatic rebuilding of backend services on code changes
- Live log streaming
- Resource monitoring
- One-click access to service endpoints

To stop the development environment:

```bash
tilt down
```

### Check setup

You might be able to find the OpenAPI specs under

- https://localhost/docs
- https://localhost:8443/docs

There's a script called `api_call.sh` that you can use to test a successful setup. The user login data is hardcoded there.

## Installation

### TODO before Prod


- code review; a second set of eyes is required
- if you must use the code as is, at least **update the user login data in `charts/titanic/values.yaml` and use proper usernames with strong passwords**
- use properly issued certificates
- a working SSO solution such as Keycloak for proper user management
  - currently handled in the app for demo puposes
- a production grade jaeger instance or equivalent for proper tracing
  - dev setup uses the all-in-one in-memory approach

### Prerequisites

- Kubernetes cluster (e.g., Docker Desktop with Kubernetes enabled)
- Helm 3.x
- kubectl

### Setup Steps

1. Add required Helm repositories:

   ```bash
   # Add Istio repository
   helm repo add istio https://istio-release.storage.googleapis.com/charts
   
   # Add cert-manager repository
   helm repo add jetstack https://charts.jetstack.io
   
   # Add Jaeger repository
   helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
   
   # Update repositories
   helm repo update
   ```

2. Create namespaces and enable Istio injection:

   ```bash
   kubectl apply -f k8s/namespaces.yaml
   ```

3. Install cert-manager:

   ```bash
   helm install cert-manager jetstack/cert-manager \
     --namespace cert-manager \
     --set installCRDs=true
   ```

4. Install Istio components:

   ```bash
   # Install Istio base
   helm install istio-base istio/base \
     --namespace istio-system

   # Install Istiod
   helm install istiod istio/istiod \
     --namespace istio-system

   # Install Istio Gateway
   helm install istio-ingressgateway istio/gateway \
     --namespace istio-system
   ```

5. Install Jaeger:

   ```bash
   helm install jaeger jaegertracing/jaeger \
     --namespace istio-system \
     --set provisionDataStore.cassandra=false \
     --set storage.type=memory \
     --set allInOne.enabled=true \
     --set collector.enabled=false \
     --set query.enabled=false \
     --set agent.enabled=false
   ```

6. Install the Titanic application:

   ```bash
   helm install titanic ./charts/titanic -n titanic-challenge
   ```

### Verification

```bash
# Verify all pods are running
kubectl get pods -n istio-system
kubectl get pods -n cert-manager
kubectl get pods -n titanic-challenge

# Access Jaeger UI (optional)
kubectl port-forward -n istio-system svc/jaeger-query 16686:16686
# Then visit http://localhost:16686
```