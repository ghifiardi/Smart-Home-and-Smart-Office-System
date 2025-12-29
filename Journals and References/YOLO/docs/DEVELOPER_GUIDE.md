# Developer Guide

**Smart Office/Home Surveillance System**

Complete guide for developers to set up, develop, and contribute to the system.

Version: 1.0.0
Last Updated: December 29, 2024

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [API Development](#api-development)
6. [Database Development](#database-development)
7. [Testing](#testing)
8. [Code Standards](#code-standards)
9. [Debugging](#debugging)
10. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

```bash
# Required
- Docker Desktop 24.0+
- Docker Compose 2.20+
- Python 3.11+
- Git 2.30+
- 8GB+ RAM
- 20GB+ disk space

# Recommended
- VS Code or PyCharm
- Postman or Insomnia (API testing)
- pgAdmin (database management)
- Redis Commander (Redis GUI)
```

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/yourorg/smartoffice-surveillance.git
cd smartoffice-surveillance

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Start infrastructure services
cd surveillance-system
docker-compose up -d postgres redis minio emqx

# 5. Run database migrations
docker exec smartoffice-auth-service alembic upgrade head

# 6. Load seed data
cd ..
./scripts/load_seed_data.sh

# 7. Start development server (example: auth service)
cd services/auth-service
uvicorn src.main:app --reload --port 8001
```

---

## Development Environment Setup

### 1. Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python --version  # Should show 3.11+
pip list
```

### 2. IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "-v",
    "--asyncio-mode=auto"
  ]
}
```

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Auth Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port", "8001"
      ],
      "cwd": "${workspaceFolder}/services/auth-service",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests",
        "-v",
        "--asyncio-mode=auto"
      ],
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

#### PyCharm

1. Open project in PyCharm
2. File → Settings → Project → Python Interpreter
3. Add virtual environment: `./venv`
4. Tools → Python Integrated Tools → Testing
5. Set default test runner to pytest

### 3. Git Configuration

```bash
# Configure Git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Install pre-commit hooks (if using pre-commit)
pip install pre-commit
pre-commit install

# Create .gitignore
cat > .gitignore <<EOF
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
EOF
```

### 4. Environment Variables

Create `.env` file in project root:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smartoffice
DB_USER=smartoffice_user
DB_PASSWORD=smartoffice_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minio_admin
MINIO_SECRET_KEY=minio_password
MINIO_SECURE=false

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=public

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
DATA_SERVICE_URL=http://localhost:8002
DETECTION_SERVICE_URL=http://localhost:8003

# Development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true
```

---

## Project Structure

```
smartoffice-surveillance/
├── services/                      # Microservices
│   ├── auth-service/
│   │   ├── src/
│   │   │   ├── main.py           # FastAPI app entry point
│   │   │   ├── api/              # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py     # Route definitions
│   │   │   │   └── deps.py       # Dependencies (auth, db)
│   │   │   ├── core/             # Core functionality
│   │   │   │   ├── config.py     # Configuration
│   │   │   │   ├── security.py   # JWT, password hashing
│   │   │   │   └── database.py   # Database connection
│   │   │   ├── models/           # Database models
│   │   │   │   └── user.py       # SQLAlchemy models
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   │   └── user.py       # Request/response schemas
│   │   │   └── services/         # Business logic
│   │   │       └── auth.py       # Auth service logic
│   │   ├── tests/                # Service tests
│   │   ├── alembic/              # Database migrations
│   │   ├── requirements.txt      # Python dependencies
│   │   └── README.md
│   │
│   ├── data-service/             # Similar structure
│   ├── detection-service/
│   ├── device-controller/
│   ├── rule-engine/
│   ├── notification-service/
│   └── analytics-service/
│
├── deployment/                    # Deployment files
│   ├── docker/                    # Dockerfiles
│   │   ├── auth-service.Dockerfile
│   │   ├── data-service.Dockerfile
│   │   └── ...
│   ├── kubernetes/                # K8s manifests
│   └── nginx/                     # Nginx configs
│
├── scripts/                       # Utility scripts
│   ├── seed_data.sql             # Sample data
│   ├── load_seed_data.sh         # Data loader
│   ├── test_services.sh          # Service health checks
│   └── tests/                     # Integration tests
│
├── docs/                          # Documentation
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── OPERATIONS_GUIDE.md
│   └── API_REFERENCE.md
│
├── surveillance-system/
│   └── docker-compose.yml        # Local development setup
│
├── requirements.txt               # Shared dependencies
├── requirements-dev.txt           # Dev dependencies
├── .env.example                   # Example environment file
├── .gitignore
└── README.md
```

---

## Development Workflow

### 1. Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/add-user-roles

# 2. Make changes
# Edit files in services/auth-service/

# 3. Run tests locally
pytest services/auth-service/tests -v

# 4. Run linting
black services/auth-service/src
flake8 services/auth-service/src

# 5. Commit changes
git add .
git commit -m "feat: add user role management"

# 6. Push to remote
git push origin feature/add-user-roles

# 7. Create pull request
# Use GitHub/GitLab UI
```

### 2. Running Services Locally

#### Option A: Docker Compose (All Services)

```bash
cd surveillance-system
docker-compose up -d
```

#### Option B: Hybrid (Infrastructure in Docker, Services Native)

```bash
# Start infrastructure
docker-compose up -d postgres redis minio emqx

# Run auth service natively (for debugging)
cd services/auth-service
uvicorn src.main:app --reload --port 8001

# Run data service in another terminal
cd services/data-service
uvicorn src.main:app --reload --port 8002
```

Benefits of hybrid approach:
- Fast reload on code changes
- Easy debugging with breakpoints
- Full IDE integration

### 3. Hot Reload Development

```bash
# FastAPI auto-reloads on file changes
uvicorn src.main:app --reload --port 8001

# Watch for changes and run tests
pytest-watch services/auth-service/tests

# Watch and format code
watchmedo shell-command \
  --patterns="*.py" \
  --recursive \
  --command='black ${watch_src_path}' \
  services/auth-service/src
```

---

## API Development

### 1. Creating a New Endpoint

**Example: Add endpoint to list user activity**

```python
# services/auth-service/src/api/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..api.deps import get_current_user, get_db
from ..schemas.activity import ActivityResponse
from ..services.activity import get_user_activity

router = APIRouter()

@router.get(
    "/api/users/me/activity",
    response_model=List[ActivityResponse],
    summary="Get current user activity",
    description="Returns activity log for the authenticated user"
)
async def get_my_activity(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity log for current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return (max 100)
    """
    try:
        activities = await get_user_activity(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=min(limit, 100)
        )
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Request/Response Schemas

```python
# services/auth-service/src/schemas/activity.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ActivityBase(BaseModel):
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource affected")
    details: Optional[dict] = Field(None, description="Additional details")

class ActivityCreate(ActivityBase):
    user_id: str

class ActivityResponse(ActivityBase):
    id: str
    user_id: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

### 3. Business Logic Layer

```python
# services/auth-service/src/services/activity.py

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta

from ..models.activity import Activity

async def get_user_activity(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    days: int = 30
) -> List[Activity]:
    """Get user activity for last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    return db.query(Activity)\
        .filter(
            Activity.user_id == user_id,
            Activity.timestamp >= cutoff_date
        )\
        .order_by(desc(Activity.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()

async def log_activity(
    db: Session,
    user_id: str,
    action: str,
    resource: str,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None
) -> Activity:
    """Log user activity"""
    activity = Activity(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
```

### 4. Database Models

```python
# services/auth-service/src/models/activity.py

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base

class Activity(Base):
    __tablename__ = "user_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # Relationship
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity {self.user_id} - {self.action}>"
```

### 5. Testing the Endpoint

```python
# services/auth-service/tests/test_activity.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_user_activity(client: AsyncClient, user_token: str):
    """Test getting user activity"""
    headers = {"Authorization": f"Bearer {user_token}"}

    response = await client.get("/api/users/me/activity", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if len(data) > 0:
        activity = data[0]
        assert "id" in activity
        assert "action" in activity
        assert "timestamp" in activity

@pytest.mark.asyncio
async def test_activity_pagination(client: AsyncClient, user_token: str):
    """Test activity pagination"""
    headers = {"Authorization": f"Bearer {user_token}"}

    # Get first page
    response1 = await client.get(
        "/api/users/me/activity?skip=0&limit=10",
        headers=headers
    )
    assert response1.status_code == 200

    # Get second page
    response2 = await client.get(
        "/api/users/me/activity?skip=10&limit=10",
        headers=headers
    )
    assert response2.status_code == 200

    # Ensure different results
    if len(response1.json()) > 0 and len(response2.json()) > 0:
        assert response1.json()[0]["id"] != response2.json()[0]["id"]
```

---

## Database Development

### 1. Creating Migrations

```bash
# Navigate to service directory
cd services/auth-service

# Create new migration
alembic revision --autogenerate -m "add user activity table"

# Review generated migration
cat alembic/versions/abc123_add_user_activity_table.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 2. Migration File Example

```python
# alembic/versions/abc123_add_user_activity_table.py

"""add user activity table

Revision ID: abc123
Revises: def456
Create Date: 2024-12-29 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'user_activity',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_activity_user_id', 'user_activity', ['user_id'])
    op.create_index('idx_activity_timestamp', 'user_activity', ['timestamp'])
    op.create_index('idx_activity_action', 'user_activity', ['action'])

def downgrade() -> None:
    op.drop_index('idx_activity_action')
    op.drop_index('idx_activity_timestamp')
    op.drop_index('idx_activity_user_id')
    op.drop_table('user_activity')
```

### 3. Database Queries

```python
# Efficient querying with SQLAlchemy

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

# Simple query
users = db.query(User).filter(User.is_active == True).all()

# With relationships (avoid N+1)
users = db.query(User)\
    .options(joinedload(User.activities))\
    .filter(User.is_active == True)\
    .all()

# Aggregation
activity_count = db.query(
    Activity.action,
    func.count(Activity.id).label('count')
)\
    .group_by(Activity.action)\
    .all()

# Complex filters
recent_admins = db.query(User)\
    .filter(
        and_(
            User.is_active == True,
            User.role == 'admin',
            User.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )\
    .all()

# Subqueries
from sqlalchemy.orm import aliased

# Find users with more than 100 activities
subq = db.query(
    Activity.user_id,
    func.count(Activity.id).label('activity_count')
)\
    .group_by(Activity.user_id)\
    .having(func.count(Activity.id) > 100)\
    .subquery()

active_users = db.query(User)\
    .join(subq, User.id == subq.c.user_id)\
    .all()
```

### 4. Using Raw SQL (when needed)

```python
from sqlalchemy import text

# Raw query
result = db.execute(
    text("""
        SELECT u.email, COUNT(a.id) as activity_count
        FROM users u
        LEFT JOIN user_activity a ON u.id = a.user_id
        WHERE u.created_at >= :since
        GROUP BY u.id, u.email
        ORDER BY activity_count DESC
        LIMIT :limit
    """),
    {"since": datetime.utcnow() - timedelta(days=7), "limit": 10}
)

top_users = result.fetchall()
```

---

## Testing

### 1. Unit Tests

```python
# services/auth-service/tests/unit/test_security.py

import pytest
from src.core.security import verify_password, hash_password, create_access_token

def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """Test JWT token creation"""
    token = create_access_token(data={"sub": "test@example.com"})

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
```

### 2. Integration Tests

```python
# services/auth-service/tests/integration/test_auth_flow.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_auth_flow(client: AsyncClient):
    """Test complete authentication flow"""

    # 1. Register user
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    response = await client.post("/api/auth/register", json=register_data)
    assert response.status_code in [200, 201]
    user_data = response.json()

    # 2. Login
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    response = await client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data

    # 3. Access protected endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == register_data["email"]

    # 4. Logout
    response = await client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
```

### 3. Test Fixtures

```python
# services/auth-service/tests/conftest.py

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.core.database import Base, get_db

# Test database
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def client(test_db):
    """Async HTTP client for testing"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def user_token(client):
    """Get auth token for testing"""
    # Register user
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    await client.post("/api/auth/register", json=register_data)

    # Login
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    response = await client.post("/api/auth/login", data=login_data)
    token_data = response.json()

    return token_data["access_token"]
```

### 4. Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest services/auth-service/tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=services/auth-service/src --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n 4

# Run and watch for changes
pytest-watch
```

---

## Code Standards

### 1. Python Style Guide

Follow PEP 8 with these additions:

```python
# Maximum line length: 100 characters
# Use 4 spaces for indentation (no tabs)

# Imports order:
# 1. Standard library
# 2. Third-party packages
# 3. Local imports

import os
import sys
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .core.config import settings
from .models.user import User

# Function naming: lowercase with underscores
def get_user_by_email(email: str) -> User:
    pass

# Class naming: PascalCase
class UserService:
    pass

# Constants: UPPERCASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Type hints for all function parameters and returns
def create_user(
    email: str,
    password: str,
    db: Session
) -> User:
    pass
```

### 2. Code Formatting

```bash
# Format code with Black
black services/auth-service/src --line-length 100

# Sort imports with isort
isort services/auth-service/src --profile black

# Check with flake8
flake8 services/auth-service/src --max-line-length 100
```

### 3. Documentation

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta. If not provided,
                       uses default from settings

    Returns:
        Encoded JWT token as string

    Raises:
        ValueError: If required claims are missing from data

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
```

### 4. Error Handling

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

async def create_user(user_data: dict, db: Session):
    """Create new user with proper error handling"""
    try:
        # Validate input
        if not user_data.get("email"):
            raise HTTPException(
                status_code=400,
                detail="Email is required"
            )

        # Create user
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created: {user.email}")
        return user

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

## Debugging

### 1. Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use throughout code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")

# Structured logging
logger.info(
    "User login",
    extra={
        "user_id": user.id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)
```

### 2. VS Code Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Auth Service",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port", "8001"
      ],
      "cwd": "${workspaceFolder}/services/auth-service",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "DEBUG": "true"
      },
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

Set breakpoints in VS Code and press F5 to start debugging.

### 3. Interactive Debugging with pdb

```python
# Add to code where you want to break
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# Common pdb commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code around current line
# q - quit debugger
```

### 4. Database Debugging

```bash
# Connect to database
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice

# Common queries
\dt                        # List tables
\d users                   # Describe users table
SELECT * FROM users;       # Query data
EXPLAIN ANALYZE SELECT ... # Query execution plan

# Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Contributing

### 1. Contribution Workflow

```bash
# 1. Fork repository on GitHub
# 2. Clone your fork
git clone https://github.com/yourusername/smartoffice-surveillance.git

# 3. Add upstream remote
git remote add upstream https://github.com/orgname/smartoffice-surveillance.git

# 4. Create feature branch
git checkout -b feature/my-new-feature

# 5. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 6. Keep branch updated
git fetch upstream
git rebase upstream/main

# 7. Push to your fork
git push origin feature/my-new-feature

# 8. Create pull request on GitHub
```

### 2. Commit Message Convention

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add password reset functionality

Implement password reset flow with email verification.
Users can now request password reset link via email.

Closes #123

---

fix(detection): resolve memory leak in video processing

Fixed memory leak caused by unclosed video capture objects.
Added proper cleanup in finally block.

---

docs(api): update API documentation for v2 endpoints

Added examples for new authentication endpoints.
Updated response schemas.
```

### 3. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)

## Related Issues
Closes #123
```

### 4. Code Review Guidelines

**As Author:**
- Keep PRs small and focused
- Write clear description
- Add tests for new functionality
- Update documentation
- Respond to feedback promptly

**As Reviewer:**
- Be constructive and respectful
- Focus on code quality, not style (automated)
- Check for security issues
- Verify tests are adequate
- Approve when satisfied

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org
- **Pytest Documentation**: https://docs.pytest.org
- **Docker Documentation**: https://docs.docker.com
- **Python Style Guide**: https://pep8.org

---

## Getting Help

- **Slack Channel**: #dev-smartoffice
- **Weekly Dev Sync**: Thursdays 10 AM
- **Documentation Issues**: Create ticket with `docs` label
- **Technical Questions**: Ask in #dev-help channel

---

**Happy Coding! 🚀**
