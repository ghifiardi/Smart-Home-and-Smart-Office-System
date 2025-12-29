# Scripts Directory Index

This directory contains all testing, seed data, and database initialization scripts for the Smart Office/Home Surveillance System.

## 📁 Directory Structure

```
scripts/
├── README.md                          # Service testing documentation
├── SEED_DATA_README.md                # Comprehensive seed data guide
├── SEED_DATA_QUICK_REFERENCE.md       # Quick reference card
├── INDEX.md                           # This file
├── init-db.sql                        # Database initialization (extensions)
├── seed_data.sql                      # Sample data for testing
├── load_seed_data.py                  # Python seed data loader
├── load_seed_data.sh                  # Bash seed data loader
├── test_services.py                   # Python service health checker
├── test_services.sh                   # Bash service health checker
└── test_requirements.txt              # Python dependencies
```

## 🎯 Quick Start Guide

### 1. Start Docker Services
```bash
docker-compose up -d
```

### 2. Load Seed Data
```bash
./scripts/load_seed_data.sh
```

### 3. Test All Services
```bash
./scripts/test_services.sh
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Service testing guide |
| `SEED_DATA_README.md` | Comprehensive seed data documentation |
| `SEED_DATA_QUICK_REFERENCE.md` | Quick reference for common tasks |
| `INDEX.md` | This overview document |

## 🔧 Script Files

### Database Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `init-db.sql` | Initialize database extensions | Auto-run by Docker |
| `seed_data.sql` | Sample data for testing | See seed data docs |
| `load_seed_data.sh` | Quick seed data loader | `./scripts/load_seed_data.sh` |
| `load_seed_data.py` | Advanced loader with options | `python3 scripts/load_seed_data.py` |

### Testing Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `test_services.sh` | Bash service health check | `./scripts/test_services.sh` |
| `test_services.py` | Python comprehensive tests | `python3 scripts/test_services.py` |
| `test_requirements.txt` | Python test dependencies | `pip install -r scripts/test_requirements.txt` |

## 🚀 Common Workflows

### Initial Setup
```bash
# 1. Start infrastructure
docker-compose up -d postgres redis minio emqx

# 2. Wait for services to be healthy
./scripts/test_services.sh

# 3. Run migrations (when available)
# alembic upgrade head

# 4. Load seed data
./scripts/load_seed_data.sh
```

### Development Testing
```bash
# Test infrastructure only
./scripts/test_services.sh | grep Infrastructure

# Reload seed data
python3 scripts/load_seed_data.py --clear

# Test specific service
curl http://localhost:8001/health
```

### Full System Test
```bash
# Build and start all services
docker-compose up -d --build

# Test everything
python3 scripts/test_services.py

# Load sample data
./scripts/load_seed_data.sh
```

## 📊 Seed Data Summary

The seed data includes:
- **7 Users** (admin, security, operators, regular users)
- **4 Sites** (Jakarta, Surabaya, Bandung, Tangerang)
- **10 Cameras** (various types and locations)
- **4 Access Control Devices**
- **5 Environmental Sensors**
- **7 Registered Persons**
- **5 Automation Rules**
- Sample historical events and detections

**Default Login:** admin@smartoffice.com / password123

## 🔍 Verification Commands

```bash
# Check Docker services
docker ps

# Test database connection
docker exec smartoffice-postgres pg_isready

# Count seed data records
docker exec smartoffice-postgres psql -U smartoffice_user -d smartoffice -c \
  "SELECT 'users' as table, COUNT(*) FROM users;"

# View all cameras
docker exec smartoffice-postgres psql -U smartoffice_user -d smartoffice -c \
  "SELECT name, ip_address, status FROM cameras;"
```

## 📖 Where to Start

1. **New to the project?** → Read `README.md`
2. **Need sample data?** → Use `load_seed_data.sh`
3. **Testing services?** → Run `test_services.sh`
4. **Need quick info?** → Check `SEED_DATA_QUICK_REFERENCE.md`
5. **Detailed docs?** → Read `SEED_DATA_README.md`

## 🆘 Troubleshooting

| Issue | Check |
|-------|-------|
| Scripts won't run | `chmod +x scripts/*.sh scripts/*.py` |
| Database connection failed | `docker ps` and check if PostgreSQL is running |
| Tables don't exist | Run database migrations first |
| Import errors (Python) | `pip install -r scripts/test_requirements.txt` |

## 📞 Getting Help

```bash
# Script help
./scripts/load_seed_data.sh --help
python3 scripts/load_seed_data.py --help

# View documentation
cat scripts/README.md
cat scripts/SEED_DATA_README.md
```

---

**Last Updated:** December 2024
