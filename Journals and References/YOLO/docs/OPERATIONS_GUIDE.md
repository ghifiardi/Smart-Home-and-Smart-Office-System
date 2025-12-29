# Operations Guide

**Smart Office/Home Surveillance System**

Complete guide for DevOps and operations teams to deploy, monitor, and maintain the system.

Version: 1.0.0
Last Updated: December 29, 2024

---

## Table of Contents

1. [Deployment](#deployment)
2. [Configuration Management](#configuration-management)
3. [Monitoring & Alerting](#monitoring--alerting)
4. [Backup & Recovery](#backup--recovery)
5. [Scaling](#scaling)
6. [Security Operations](#security-operations)
7. [Maintenance](#maintenance)
8. [Incident Response](#incident-response)
9. [Performance Tuning](#performance-tuning)
10. [Troubleshooting](#troubleshooting)

---

## Deployment

### Production Deployment Options

#### Option 1: Docker Compose (Small Scale)

**Use Case:** Single server, < 10 cameras, < 100 users

```bash
# 1. Clone repository
git clone https://github.com/yourorg/smartoffice-surveillance.git
cd smartoffice-surveillance

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Start services
cd surveillance-system
docker-compose -f docker-compose.prod.yml up -d

# 4. Run migrations
docker exec smartoffice-auth-service alembic upgrade head

# 5. Create admin user
docker exec -it smartoffice-auth-service python scripts/create_admin.py

# 6. Verify deployment
curl https://your-domain.com/health
```

**Production docker-compose.yml:**

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    restart: always
    depends_on:
      - auth-service
      - data-service

  auth-service:
    build:
      context: ..
      dockerfile: deployment/docker/auth-service.Dockerfile
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
      - ENV=production
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: always
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

#### Option 2: Kubernetes (Medium to Large Scale)

**Use Case:** Multi-server, 10+ cameras, 100+ users, high availability

```bash
# 1. Prepare Kubernetes cluster
kubectl cluster-info

# 2. Create namespace
kubectl create namespace smartoffice

# 3. Create secrets
kubectl create secret generic db-credentials \
  --from-literal=username=smartoffice_user \
  --from-literal=password=your-secure-password \
  -n smartoffice

kubectl create secret generic jwt-secret \
  --from-literal=secret-key=your-jwt-secret-key \
  -n smartoffice

# 4. Deploy infrastructure
kubectl apply -f deployment/kubernetes/infrastructure/

# 5. Deploy services
kubectl apply -f deployment/kubernetes/services/

# 6. Verify deployment
kubectl get pods -n smartoffice
kubectl get svc -n smartoffice

# 7. Run migrations
kubectl exec -it deployment/auth-service -n smartoffice -- \
  alembic upgrade head
```

**Kubernetes Deployment Example (Auth Service):**

```yaml
# deployment/kubernetes/services/auth-service.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: smartoffice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: yourregistry.com/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: postgres-service
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: smartoffice
spec:
  selector:
    app: auth-service
  ports:
  - port: 8001
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth-service-hpa
  namespace: smartoffice
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

#### Option 3: Cloud Managed Services (AWS/GCP/Azure)

**AWS Deployment Example:**

```bash
# Infrastructure as Code (Terraform)

# 1. Configure AWS credentials
aws configure

# 2. Initialize Terraform
cd deployment/terraform/aws
terraform init

# 3. Plan deployment
terraform plan -out=tfplan

# 4. Apply changes
terraform apply tfplan

# 5. Get outputs
terraform output -json > outputs.json
```

**Terraform Configuration:**

```hcl
# deployment/terraform/aws/main.tf

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "smartoffice-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "smartoffice-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "smartoffice-db"
  engine = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.large"
  allocated_storage = 100
  storage_type = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  multi_az = true
  backup_retention_period = 7
  backup_window = "03:00-04:00"

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name = aws_db_subnet_group.main.name

  tags = {
    Name = "smartoffice-postgres"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id = "smartoffice-redis"
  engine = "redis"
  engine_version = "7.0"
  node_type = "cache.t3.medium"
  num_cache_nodes = 1
  parameter_group_name = "default.redis7"
  port = 6379

  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  snapshot_retention_limit = 5
  snapshot_window = "03:00-05:00"

  tags = {
    Name = "smartoffice-redis"
  }
}

# S3 for object storage
resource "aws_s3_bucket" "storage" {
  bucket = "smartoffice-storage-${var.environment}"

  tags = {
    Name = "smartoffice-storage"
  }
}

resource "aws_s3_bucket_versioning" "storage" {
  bucket = aws_s3_bucket.storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ECS Task Definition (Auth Service)
resource "aws_ecs_task_definition" "auth_service" {
  family = "auth-service"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "512"
  memory = "1024"

  container_definitions = jsonencode([{
    name = "auth-service"
    image = "${var.ecr_repository}/auth-service:latest"
    portMappings = [{
      containerPort = 8000
      protocol = "tcp"
    }]
    environment = [
      {
        name = "DB_HOST"
        value = aws_db_instance.postgres.endpoint
      },
      {
        name = "REDIS_HOST"
        value = aws_elasticache_cluster.redis.cache_nodes[0].address
      }
    ]
    secrets = [
      {
        name = "DB_PASSWORD"
        valueFrom = aws_secretsmanager_secret_version.db_password.arn
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group" = "/ecs/auth-service"
        "awslogs-region" = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ECS Service
resource "aws_ecs_service" "auth_service" {
  name = "auth-service"
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.auth_service.arn
  desired_count = 3
  launch_type = "FARGATE"

  network_configuration {
    subnets = aws_subnet.private[*].id
    security_groups = [aws_security_group.app.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.auth.arn
    container_name = "auth-service"
    container_port = 8000
  }

  depends_on = [aws_lb_listener.https]
}

# Application Load Balancer
resource "aws_lb" "main" {
  name = "smartoffice-alb"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.alb.id]
  subnets = aws_subnet.public[*].id

  enable_deletion_protection = true

  tags = {
    Name = "smartoffice-alb"
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name = "auth-service-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods = "2"
  metric_name = "CPUUtilization"
  namespace = "AWS/ECS"
  period = "60"
  statistic = "Average"
  threshold = "80"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.auth_service.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

---

## Configuration Management

### Environment Variables

**Production .env template:**

```bash
# Environment
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DB_HOST=postgres-prod.example.com
DB_PORT=5432
DB_NAME=smartoffice_prod
DB_USER=smartoffice_user
DB_PASSWORD=<use-secrets-manager>
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_HOST=redis-prod.example.com
REDIS_PORT=6379
REDIS_PASSWORD=<use-secrets-manager>
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50

# MinIO/S3
S3_ENDPOINT=s3.amazonaws.com
S3_BUCKET=smartoffice-storage-prod
S3_ACCESS_KEY=<use-secrets-manager>
S3_SECRET_KEY=<use-secrets-manager>
S3_REGION=us-east-1

# MQTT
MQTT_BROKER=mqtt-prod.example.com
MQTT_PORT=8883
MQTT_USERNAME=<use-secrets-manager>
MQTT_PASSWORD=<use-secrets-manager>
MQTT_TLS=true
MQTT_CA_CERT=/etc/ssl/certs/ca-bundle.crt

# JWT
JWT_SECRET_KEY=<use-secrets-manager>
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=/etc/ssl/certs/jwt-public.pem
JWT_PRIVATE_KEY_PATH=/etc/ssl/certs/jwt-private.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=https://dashboard.example.com,https://mobile.example.com
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<use-secrets-manager>
SMTP_FROM=noreply@example.com

# Monitoring
SENTRY_DSN=<sentry-dsn>
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Feature Flags
ENABLE_FACE_RECOGNITION=true
ENABLE_ANALYTICS=true
ENABLE_NOTIFICATIONS=true
```

### Secrets Management

#### Using AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name smartoffice/prod/db-password \
  --secret-string "your-secure-password"

# Retrieve secret
aws secretsmanager get-secret-value \
  --secret-id smartoffice/prod/db-password \
  --query SecretString \
  --output text

# Update secret
aws secretsmanager update-secret \
  --secret-id smartoffice/prod/db-password \
  --secret-string "new-password"
```

**Application integration:**

```python
# services/auth-service/src/core/config.py

import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str) -> str:
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise Exception(f"Error retrieving secret: {e}")

# Usage
DB_PASSWORD = get_secret('smartoffice/prod/db-password')
JWT_SECRET_KEY = get_secret('smartoffice/prod/jwt-secret')
```

---

## Monitoring & Alerting

### Metrics Collection (Prometheus)

**Prometheus configuration:**

```yaml
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:9090']
    metrics_path: '/metrics'

  - job_name: 'data-service'
    static_configs:
      - targets: ['data-service:9090']

  - job_name: 'detection-service'
    static_configs:
      - targets: ['detection-service:9090']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

**Application metrics:**

```python
# services/auth-service/src/core/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
ACTIVE_USERS = Gauge(
    'active_users_total',
    'Total active users'
)

LOGIN_ATTEMPTS = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status']  # success, failed
)

# Usage in middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

### Grafana Dashboards

**System Overview Dashboard:**

```json
{
  "dashboard": {
    "title": "Smart Office - System Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
        }]
      },
      {
        "title": "Active Users",
        "targets": [{
          "expr": "active_users_total"
        }]
      }
    ]
  }
}
```

### Alerting Rules

**Prometheus alert rules:**

```yaml
# alerts.yml

groups:
  - name: smartoffice_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} per second"

      # High response time
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }}s"

      # Database connection issues
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          description: "PostgreSQL database is not responding"

      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"

      # Disk space low
      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low"
          description: "Disk usage is {{ $value }}%"
```

**AlertManager configuration:**

```yaml
# alertmanager.yml

global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: '<password>'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-ops'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'team-ops'
    email_configs:
      - to: 'ops-team@example.com'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty-service-key>'
```

### Application Logging

**Centralized logging with ELK Stack:**

```yaml
# filebeat.yml

filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "smartoffice-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

**Structured logging format:**

```python
import structlog

logger = structlog.get_logger()

# Log with context
logger.info(
    "user_login",
    user_id=user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    success=True
)
```

---

## Backup & Recovery

### Database Backups

**Automated backup script:**

```bash
#!/bin/bash
# scripts/backup_database.sh

set -e

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="smartoffice_${TIMESTAMP}.sql.gz"

# Create backup
docker exec smartoffice-postgres pg_dump \
  -U smartoffice_user \
  smartoffice \
  | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" \
  "s3://smartoffice-backups/database/${BACKUP_FILE}"

# Keep only last 30 days locally
find "${BACKUP_DIR}" -type f -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**Schedule with cron:**

```bash
# Run daily at 2 AM
0 2 * * * /path/to/scripts/backup_database.sh
```

### Database Restore

```bash
#!/bin/bash
# Restore from backup

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

# Stop applications
docker-compose stop auth-service data-service

# Restore database
gunzip -c "$BACKUP_FILE" | \
  docker exec -i smartoffice-postgres psql \
  -U smartoffice_user \
  -d smartoffice

# Start applications
docker-compose start auth-service data-service

echo "Restore completed"
```

### Object Storage Backup

```bash
#!/bin/bash
# Backup MinIO/S3 data

SOURCE_BUCKET="smartoffice-recordings"
BACKUP_BUCKET="smartoffice-backups"
TIMESTAMP=$(date +%Y%m%d)

# Sync to backup bucket
aws s3 sync \
  "s3://${SOURCE_BUCKET}/" \
  "s3://${BACKUP_BUCKET}/recordings-${TIMESTAMP}/" \
  --storage-class GLACIER

echo "Object storage backup completed"
```

---

## Scaling

### Horizontal Scaling

**Auto-scaling with Kubernetes:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

### Database Scaling

**Read replicas configuration:**

```yaml
# PostgreSQL replication

# Primary server (postgresql.conf)
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
hot_standby = on

# Replica server
hot_standby = on
hot_standby_feedback = on
```

**Application configuration for read replicas:**

```python
# Database connection pooling

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from random import choice

# Primary (write)
PRIMARY_DB_URL = "postgresql://user:pass@primary:5432/smartoffice"
primary_engine = create_engine(PRIMARY_DB_URL, pool_size=20)

# Replicas (read)
REPLICA_DB_URLS = [
    "postgresql://user:pass@replica1:5432/smartoffice",
    "postgresql://user:pass@replica2:5432/smartoffice",
]
replica_engines = [
    create_engine(url, pool_size=20) for url in REPLICA_DB_URLS
]

def get_read_engine():
    """Get random read replica"""
    return choice(replica_engines)

def get_write_engine():
    """Get primary database for writes"""
    return primary_engine
```

---

## Security Operations

### SSL/TLS Configuration

**Nginx SSL configuration:**

```nginx
# nginx/nginx.conf

server {
    listen 443 ssl http2;
    server_name smartoffice.example.com;

    # SSL certificates
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://auth-service:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Scanning

```bash
# Container vulnerability scanning
docker scan smartoffice/auth-service:latest

# Dependency scanning
pip install safety
safety check -r requirements.txt

# Code security analysis
pip install bandit
bandit -r services/auth-service/src
```

### Audit Logging

```python
# Audit log implementation

from datetime import datetime
import json

async def log_audit_event(
    user_id: str,
    action: str,
    resource: str,
    details: dict,
    ip_address: str
):
    """Log security audit event"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details,
        "ip_address": ip_address
    }

    # Write to audit log file
    with open("/var/log/audit/security.log", "a") as f:
        f.write(json.dumps(event) + "\n")

    # Also store in database
    await store_audit_event(event)
```

---

## Performance Tuning

### Database Optimization

```sql
-- Create appropriate indexes
CREATE INDEX CONCURRENTLY idx_events_timestamp
  ON events(timestamp DESC);

CREATE INDEX CONCURRENTLY idx_events_camera
  ON events(camera_id, timestamp DESC);

-- Analyze tables
ANALYZE events;
ANALYZE users;

-- Vacuum
VACUUM ANALYZE;

-- Configure PostgreSQL
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '32MB';
```

### Redis Optimization

```bash
# redis.conf

maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### Application Tuning

```python
# Connection pooling
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Number of persistent connections
    max_overflow=10,        # Additional connections when pool exhausted
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False              # Disable SQL logging in production
)

# Async workers for FastAPI
uvicorn_config = {
    "workers": 4,           # CPU cores
    "worker_class": "uvicorn.workers.UvicornWorker",
    "timeout": 120,
    "keepalive": 5,
}
```

---

**Continue to Incident Response, Troubleshooting, and more in the next sections...**

For complete Operations Guide, see the full documentation.
