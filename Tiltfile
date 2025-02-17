# Set allowed k8s context
allow_k8s_contexts('docker-desktop')

# Install Istio
load('ext://helm_resource', 'helm_resource', 'helm_repo')
load('ext://namespace', 'namespace_create')

# Add Istio helm repository
helm_repo('istio', 'https://istio-release.storage.googleapis.com/charts')

namespace_create('istio-system')

helm_resource(
    'istio-base',
    chart='istio/base',
    namespace='istio-system'
)

helm_resource(
    'istiod',
    chart='istio/istiod',
    namespace='istio-system'
)

helm_resource(
    'istio-ingressgateway',
    chart='istio/gateway',
    namespace='istio-system'
)

# Create namespace for the application
k8s_yaml('k8s/namespace.yaml')

# Enable experimental features
load('ext://uibutton', 'cmd_button')

# Docker build settings
docker_build(
    'titanic-api',
    'api',
    dockerfile='api/Dockerfile',
    live_update=[
        sync('api', '/app'),
        run('pip install -r requirements.txt', trigger='requirements.txt')
    ]
)

# Kubernetes deployment
k8s_yaml(['k8s/deployment.yaml', 'k8s/service.yaml', 'k8s/gateway.yaml'])

# Resource configuration
k8s_resource(
    'titanic-api',
    port_forwards=['8000:8000'],
    labels=['api']
)

k8s_resource(
    'istio-ingressgateway',
    port_forwards=['8443:443'],
    labels=['gateway']
)

# Add auth policy
k8s_yaml('api/k8s/auth-policy.yaml')

# Add convenient UI buttons
cmd_button(
    'pytest',
    'pytest',
    text='Run Tests',
    icon_name='bug_report',
    argv=['pytest']
)

# Certificate management
load('ext://secret', 'secret_yaml_tls')

def generate_certs():
    local('mkdir -p k8s/certs')
    local('./k8s/scripts/generate-cert.sh k8s/certs')
    return 'k8s/certs/tls.crt', 'k8s/certs/tls.key'

# Create TLS secret using secret_yaml_tls
cert_path, key_path = generate_certs()
k8s_yaml(secret_yaml_tls(
    'titanic-credential',
    cert_path,
    key_path,
    'istio-system'
))
