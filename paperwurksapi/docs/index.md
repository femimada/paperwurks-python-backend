# Paperwurks Backend API

Django REST API backend for Paperwurks property conveyancing platform. Provides document processing, AI analysis, and search ordering capabilities.

## Tech Stack

- **Framework**: Django 5.1 with Django Ninja
- **Database**: PostgreSQL 15
- **Cache/Broker**: Redis 7.1 (AWS ElastiCache)
- **Task Queue**: Celery 5.3
- **Storage**: AWS S3
- **Deployment**: AWS Fargate (ECS)

## Project Structure

```
paperwurksapi/
├── apps/
│   ├── config/          # Django settings and configuration
│   │   ├── settings/
│   │   │   ├── common.py      # Shared settings
│   │   │   ├── development.py # Local development
│   │   │   ├── staging.py     # Staging environment
│   │   │   └── production.py  # Production environment
│   │   ├── celery.py    # Celery configuration
│   │   ├── urls.py      # URL routing
│   │   └── wsgi.py      # WSGI application
│   └── users/           # User management app
├── requirements/
│   ├── base.in          # Core dependencies
│   ├── dev.in           # Development dependencies
│   └── prod.in          # Production dependencies
├── scripts/
│   └── entrypoint.sh    # Container entrypoint
├── docker-compose.dev.yml
├── Dockerfile
└── manage.py
```

## Prerequisites

- **Docker** and **Docker Compose** (for local development)
- **Python 3.12+** (if running without Docker)
- **PostgreSQL 15** (if running locally without Docker)
- **Redis 7** (if running locally without Docker)

## Local Development

### Quick Start

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd paperwurksapi
   ```

2. **Start all services**

   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Admin: http://localhost:8000/admin

### Development Services

The development environment includes:

- **backend**: Django API server with hot-reload
- **worker**: Celery worker for async tasks
- **postgres**: PostgreSQL 15 database
- **redis**: Redis 7 (cache + Celery broker)
- **localstack**: AWS service emulation (S3, etc.)

### Common Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Run migrations
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

# Run tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Access Django shell
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

## Environment Variables

### Local Development (Docker Compose)

All environment variables are defined in `docker-compose.dev.yml`. Key variables:

```bash
# Django
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DJANGO_SETTINGS_MODULE=apps.config.settings.development

# Database (connects to postgres service)
DB_NAME=paperwurks_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis/Celery (connects to redis service)
REDIS_URL=redis://:devpassword@redis:6379/0
CELERY_BROKER_URL=redis://:devpassword@redis:6379/0
CELERY_RESULT_BACKEND=redis://:devpassword@redis:6379/0

# AWS (uses LocalStack)
AWS_ENDPOINT_URL=http://localstack:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=eu-west-2
AWS_STORAGE_BUCKET_NAME=paperwurks-dev-documents

# API
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### AWS Deployment (ECS Fargate)

In AWS environments (dev/staging/production), all configuration is automatically injected as environment variables by the ECS Task Execution Role from:

- **AWS Secrets Manager** (sensitive data)
- **AWS Systems Manager Parameter Store** (non-sensitive configuration)

#### From Secrets Manager

```bash
# Automatically injected by ECS
SECRET_KEY          # Django secret key (50 chars, randomly generated)
DATABASE_URL        # PostgreSQL connection string
                    # Format: postgresql://user:pass@host:port/dbname?sslmode=require&connect_timeout=10
```

#### From Parameter Store

```bash
# Environment Configuration
ENVIRONMENT                  # development | staging | production
DEBUG                        # True | False
DJANGO_SETTINGS_MODULE       # apps.config.settings.{environment}
LOG_LEVEL                    # DEBUG | INFO | WARNING | ERROR

# Network Configuration
ALLOWED_HOSTS                # Comma-separated: alb-*.elb.amazonaws.com,api.paperwurks.co.uk
CORS_ALLOWED_ORIGINS         # Comma-separated frontend URLs

# Redis/Celery (TLS-enabled URLs)
REDIS_URL                    # rediss://:auth_token@endpoint:6379/0
CELERY_BROKER_URL            # rediss://:auth_token@endpoint:6379/0
CELERY_RESULT_BACKEND        # rediss://:auth_token@endpoint:6379/0

# AWS Services
AWS_REGION                   # eu-west-2
AWS_STORAGE_BUCKET_NAME      # paperwurks-{env}-documents

# Feature Flags
ENABLE_AI_ANALYSIS           # True | False
ENABLE_DOCUMENT_PROCESSING   # True | False
ENABLE_SEARCH_INTEGRATION    # True | False

# Production Security (prod only)
CSRF_TRUSTED_ORIGINS         # Comma-separated trusted origins
SECURE_SSL_REDIRECT          # True
SESSION_COOKIE_SECURE        # True
CSRF_COOKIE_SECURE           # True
SECURE_HSTS_SECONDS          # 31536000
```

**Note**: The application uses `python-decouple` to read these environment variables. No boto3 SDK calls are needed - ECS handles injection automatically.

## Configuration by Environment

### Development

- **Database**: SQLite (fallback) or PostgreSQL via Docker
- **Redis**: Local Redis container (no TLS)
- **Storage**: Local filesystem or LocalStack S3
- **Debug**: Enabled
- **Hot-reload**: Enabled

### Staging

- **Database**: RDS PostgreSQL (db.t3.small, single-AZ)
- **Redis**: ElastiCache (cache.t4g.micro, single node, TLS enabled)
- **Storage**: S3 with lifecycle policies
- **Debug**: Enabled (for troubleshooting)
- **Security**: Basic (no HSTS)

### Production

- **Database**: RDS PostgreSQL (db.t3.medium, Multi-AZ)
- **Redis**: ElastiCache (cache.t4g.small, Multi-AZ with replica, TLS enabled)
- **Storage**: S3 with versioning and encryption
- **Debug**: Disabled
- **Security**: Full enforcement (HSTS, secure cookies, SSL redirect)

## Database

### Migrations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Connection Details

The application uses `dj-database-url` to parse `DATABASE_URL` environment variable:

- **Local**: SQLite or PostgreSQL via Docker Compose
- **AWS**: RDS PostgreSQL with SSL required

Format: `postgresql://user:password@host:port/dbname?sslmode=require&connect_timeout=10`

## Celery Tasks

### Running Celery Worker

```bash
# Development (Docker Compose)
# Worker runs automatically as separate service

# Standalone worker (without Docker)
celery -A apps.config worker -l info
```

### Task Queues

- `document_processing`: Document upload and processing tasks
- `ai_analysis`: AI-powered document analysis
- `search_ordering`: Property search and ordering
- `notifications`: Email and notification tasks

### Monitoring Tasks

```bash
# Check running tasks
celery -A apps.config inspect active

# Check registered tasks
celery -A apps.config inspect registered

# Purge all tasks (development only)
celery -A apps.config purge
```

## Testing

### Run Tests

```bash
# All tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# With coverage
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=apps

# Specific test file
docker-compose -f docker-compose.dev.yml exec backend pytest apps/users/tests/test_models.py

# Run with verbose output
docker-compose -f docker-compose.dev.yml exec backend pytest -v
```

### Test Structure

```
apps/
└── users/
    ├── tests/
    │   ├── __init__.py
    │   ├── test_models.py
    │   ├── test_views.py
    │   └── test_tasks.py
```

## API Documentation

- **Interactive Docs**: http://localhost:8000/api/docs (Swagger UI)
- **API Schema**: http://localhost:8000/api/openapi.json

The API is built with Django Ninja, providing automatic OpenAPI/Swagger documentation.

## Dependencies

### Core Dependencies (requirements/base.in)

```
Django>=5.1,<5.2          # Web framework
django-ninja>=1.4         # REST API framework
psycopg2-binary>=2.9      # PostgreSQL driver
celery>=5.3               # Task queue
redis>=5.0                # Redis client (with SSL support)
dj-database-url>=2.0      # Database URL parsing
python-decouple>=3.8      # Environment variable management
django-cors-headers>=4.3  # CORS handling
gunicorn>=23.0            # Production WSGI server
```

### Development Dependencies (requirements/dev.in)

```
pytest>=8.0
pytest-django
pytest-cov
django-debug-toolbar
django-extensions
```

### Production Dependencies (requirements/prod.in)

```
boto3>=1.34               # AWS SDK (for S3)
django-storages>=1.14     # S3 storage backend
```

### Installing Dependencies

```bash
# Install base + dev dependencies
pip install -r requirements/base.txt -r requirements/dev.txt

# Install production dependencies
pip install -r requirements/prod.txt
```

## Deployment

The application is deployed to AWS ECS Fargate via GitHub Actions CI/CD pipeline.

### Deployment Flow

1. **Push to branch** → GitHub Actions triggered
2. **Build Docker image** → Tagged with commit SHA
3. **Push to ECR** → AWS Elastic Container Registry
4. **Update ECS task definition** → New image reference
5. **Deploy to ECS** → Rolling update with health checks

### Deployment Environments

- **Development**: Deploys on push to `develop` branch
- **Staging**: Deploys on push to `staging` branch
- **Production**: Deploys on push to `main` branch

### Manual Deployment

```bash
# Build production image
docker build --target production -t paperwurks-backend:latest .

# Tag for ECR
docker tag paperwurks-backend:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/paperwurks-backend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/paperwurks-backend:latest

# Update ECS service (forces new deployment)
aws ecs update-service --cluster prod-paperwurks-cluster \
  --service prod-paperwurks-backend --force-new-deployment
```

## Troubleshooting

### Database Connection Issues

```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection from container
docker-compose exec backend python manage.py dbshell
```

### Redis Connection Issues

```bash
# Check Redis URL (local dev uses redis://, AWS uses rediss:// with TLS)
echo $REDIS_URL

# Test Redis connection
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Celery Not Processing Tasks

```bash
# Check worker logs
docker-compose logs -f worker

# Verify Redis connection
docker-compose exec worker celery -A apps.config inspect ping

# Check active tasks
docker-compose exec worker celery -A apps.config inspect active
```

### AWS ECS Task Failures

```bash
# View ECS task logs
aws logs tail /ecs/dev-paperwurks-backend --follow

# Check task stopped reason
aws ecs describe-tasks --cluster dev-paperwurks-cluster --tasks <task-id>

# Verify secrets and parameters exist
aws secretsmanager get-secret-value --secret-id paperwurks/dev/django
aws ssm get-parameter --name /paperwurks/dev/django/DEBUG
```

## Security Considerations

### Production Security Checklist

- AS`DEBUG=False` in production
- ASStrong `SECRET_KEY` (generated by Terraform)
- AS`ALLOWED_HOSTS` configured correctly
- ASDatabase uses SSL (`sslmode=require`)
- ASRedis uses TLS (`rediss://` scheme)
- ASCORS properly configured
- ASCSRF protection enabled
- ASHSTS enabled in production
- ASSecure cookies (HTTPS only)
- ASS3 bucket encryption enabled
- ASSecrets stored in AWS Secrets Manager
- ASIAM roles follow least privilege

### Secrets Management

**Never commit secrets to Git!**

- Local development: Use `.env` files (not committed)
- AWS environments: Secrets Manager + Parameter Store
- CI/CD: GitHub Secrets for AWS credentials

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Write/update tests
4. Run tests locally: `pytest`
5. Push and create a Pull Request
6. Wait for CI/CD checks to pass
7. Request code review

## Support

- **Infrastructure Issues**: Check `paperwurks-infrastructure` repository
- **API Documentation**: http://localhost:8000/api/docs
- **Logs**: CloudWatch Logs (AWS) or `docker-compose logs` (local)

## License

Proprietary - Paperwurks Ltd.
