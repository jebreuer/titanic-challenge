update_settings(k8s_upsert_timeout_secs = 120)

# Set allowed k8s context
allow_k8s_contexts('docker-desktop')

# Create namespaces first
k8s_yaml('k8s/namespaces.yaml')

# Load Helm extensions
load('ext://helm_resource', 'helm_resource', 'helm_repo')
load('ext://namespace', 'namespace_create')

# Add Helm repositories
helm_repo('istio', 'https://istio-release.storage.googleapis.com/charts')
helm_repo('jetstack', 'https://charts.jetstack.io')
helm_repo('jaegertracing', 'https://jaegertracing.github.io/helm-charts')

# Create required namespaces
namespace_create('istio-system')
namespace_create('cert-manager')

# Install cert-manager
helm_resource(
    'cert-manager',
    'jetstack/cert-manager',
    namespace='cert-manager',
    flags=['--set', 'installCRDs=true'],
)

# Certificate management
k8s_yaml('k8s/certificates.yaml')

# Install Istio
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
k8s_yaml([
    'k8s/deployment.yaml',
    'k8s/service.yaml',
    'k8s/gateway.yaml',
    'k8s/auth-secret.yaml'
])

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
k8s_yaml('k8s/auth-policy.yaml')

# Add convenient UI buttons
cmd_button(
    'pytest',
    'pytest',
    text='Run Tests',
    icon_name='bug_report',
    argv=['pytest']
)

# Install Jaeger (both operator and instance)
helm_resource(
    'jaeger',
    'jaegertracing/jaeger',
    namespace='istio-system',
    resource_deps=['cert-manager'],
    flags=[
        '--set', 'provisionDataStore.cassandra=false',
        '--set', 'storage.type=memory',
        '--set', 'allInOne.enabled=true',
        '--set', 'collector.enabled=false',
        '--set', 'query.enabled=false',
        '--set', 'agent.enabled=false',
    ]
)

# Resource configuration
k8s_resource(
    'jaeger',
    port_forwards=['16686:16686'],
    labels=['observability']
)
