# Seed Data Quick Reference Card

## 🚀 Quick Commands

```bash
# Load seed data (easiest)
./scripts/load_seed_data.sh

# Load with Python
python3 scripts/load_seed_data.py

# Clear and reload
python3 scripts/load_seed_data.py --clear
```

## 🔐 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@smartoffice.com | password123 |
| **Security** | security@smartoffice.com | password123 |
| **Operator** | operator@smartoffice.com | password123 |
| **User** | john.doe@smartoffice.com | password123 |

⚠️ **CHANGE THESE IN PRODUCTION!**

## 📊 What Gets Created

| Resource | Count | Description |
|----------|-------|-------------|
| **Users** | 7 | Various roles and permissions |
| **Sites** | 4 | Jakarta, Surabaya, Bandung, Tangerang |
| **Buildings** | 4 | Office towers and warehouses |
| **Zones** | 9 | Lobbies, offices, parking, storage |
| **Cameras** | 10 | IP and PTZ cameras (mix of online/offline) |
| **Access Devices** | 4 | Card readers, biometric scanners |
| **Sensors** | 5 | Temperature, humidity, motion, air quality |
| **Persons** | 7 | Employees, contractors, visitors |
| **Rules** | 5 | Automation and alert rules |
| **Events** | Sample | Last 7 days of activity |

## 🎯 Sample Cameras

```
Lobby:           192.168.1.101-102  (4K)
Executive:       192.168.1.201      (PTZ)
IT:              192.168.1.501      (5MP)
Parking:         192.168.1.151-152  (4K)
Cafeteria:       192.168.1.301      (1080p)
Warehouse:       192.168.2.101-102  (4K/5MP)
```

## 📍 Sample Locations

### Jakarta HQ
- Main Tower: 20 floors
- Zones: Lobby, Executive, IT, Meeting Rooms, Cafeteria, Parking

### Tangerang Warehouse
- Storage Facility 1
- Zones: Storage Area, Loading Dock

## 🔍 Verify Data

```bash
# Check if data loaded
docker exec smartoffice-postgres psql -U smartoffice_user -d smartoffice -c "
SELECT 'users' as table, COUNT(*) FROM users
UNION ALL SELECT 'cameras', COUNT(*) FROM cameras
UNION ALL SELECT 'sensors', COUNT(*) FROM sensors;"
```

## 🧪 Testing Scenarios

### Test Authentication
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartoffice.com","password":"password123"}'
```

### Test Camera Access
```bash
curl http://localhost:8003/api/cameras
```

### Test Zones
```bash
curl http://localhost:8002/api/zones
```

## 📋 Common Tasks

**Load fresh seed data:**
```bash
./scripts/load_seed_data.sh
```

**Backup before reloading:**
```bash
docker exec smartoffice-postgres pg_dump -U smartoffice_user smartoffice > backup.sql
python3 scripts/load_seed_data.py --clear
```

**Check specific camera:**
```sql
SELECT name, ip_address, status
FROM cameras
WHERE name LIKE '%Lobby%';
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Tables don't exist | Run migrations first: `alembic upgrade head` |
| Connection refused | Start Docker: `docker-compose up -d` |
| Duplicate keys | Use `--clear` flag or delete manually |
| Permission denied | Check database user permissions |

## 📞 Quick Help

```bash
# Python script help
python3 scripts/load_seed_data.py --help

# View seed data file
cat scripts/seed_data.sql

# Full documentation
cat scripts/SEED_DATA_README.md
```

---

**Need more help?** See `SEED_DATA_README.md` for comprehensive documentation.
