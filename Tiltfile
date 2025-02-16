# Set allowed k8s context
allow_k8s_contexts('docker-desktop')

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
k8s_yaml('k8s/deployment.yaml')
k8s_yaml('k8s/service.yaml')

# Resource configuration
k8s_resource(
    'titanic-api',
    port_forwards='8000:8000',
    labels=['api']
)

# Add convenient UI buttons
cmd_button(
    'pytest',
    'pytest',
    text='Run Tests',
    icon_name='bug_report',
    argv=['pytest']
)
