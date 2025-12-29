# Smart Office/Home Seed Data Documentation

This directory contains seed data scripts for populating the Smart Office/Home Surveillance System database with sample data for testing and development.

## 📁 Files

- **`seed_data.sql`** - SQL script with all seed data
- **`load_seed_data.py`** - Python script to load seed data with verification
- **`load_seed_data.sh`** - Bash script for quick loading

## 🚀 Quick Start

### Option 1: Using Bash Script (Easiest)

```bash
./scripts/load_seed_data.sh
```

### Option 2: Using Python Script (More Control)

```bash
# Install dependencies (if not already installed)
pip install psycopg2-binary

# Load seed data
python3 scripts/load_seed_data.py

# Load with custom database
python3 scripts/load_seed_data.py --host localhost --database mydb --user myuser
```

### Option 3: Direct SQL Loading

```bash
# Using Docker
docker exec -i smartoffice-postgres psql -U smartoffice_user -d smartoffice < scripts/seed_data.sql

# Using local psql
psql -h localhost -U smartoffice_user -d smartoffice -f scripts/seed_data.sql
```

## 📊 Seed Data Contents

### 1. Users (7 total)

| Email | Username | Role | Password |
|-------|----------|------|----------|
| admin@smartoffice.com | admin | Administrator | password123 |
| security@smartoffice.com | security_manager | Security Manager | password123 |
| operator@smartoffice.com | operator1 | Operator | password123 |
| john.doe@smartoffice.com | johndoe | User | password123 |
| jane.smith@smartoffice.com | janesmith | User | password123 |
| mike.wilson@smartoffice.com | mikewilson | User | password123 |
| guest@smartoffice.com | guest | Guest | password123 |

**⚠️ Important:** All passwords are hashed with bcrypt. Change these in production!

### 2. Sites (4 locations)

1. **HQ Building - Jakarta**
   - Address: Jl. Sudirman No. 123, Jakarta
   - Buildings: Main Tower (20 floors), Annex Building (5 floors)

2. **Branch Office - Surabaya**
   - Address: Jl. Basuki Rahmat No. 45, Surabaya
   - Buildings: Office Block A (8 floors)

3. **Branch Office - Bandung**
   - Address: Jl. Asia Afrika No. 78, Bandung

4. **Warehouse - Tangerang**
   - Address: Jl. Raya Serpong No. 99, Tangerang
   - Buildings: Storage Facility 1

### 3. Zones (9 total)

- Main Lobby (Public)
- Executive Floor (Restricted)
- IT Department (Restricted)
- Meeting Room A (Restricted)
- Cafeteria (Public)
- Parking Basement (Public)
- Training Room (Restricted)
- Storage Area 1 (Restricted)
- Loading Dock (Restricted)

### 4. Cameras (10 total)

| Camera Name | Type | Zone | IP Address | Resolution | Status |
|-------------|------|------|------------|------------|--------|
| Lobby Entrance CAM-001 | IP | Main Lobby | 192.168.1.101 | 4K | Online |
| Lobby Reception CAM-002 | IP | Main Lobby | 192.168.1.102 | 4K | Online |
| Executive Hallway CAM-201 | PTZ | Executive Floor | 192.168.1.201 | 1080p | Online |
| IT Server Room CAM-501 | IP | IT Department | 192.168.1.501 | 5MP | Online |
| Parking Entry CAM-B01 | IP | Parking Basement | 192.168.1.151 | 4K | Online |
| Parking Exit CAM-B02 | IP | Parking Basement | 192.168.1.152 | 4K | Online |
| Cafeteria Main CAM-C01 | IP | Cafeteria | 192.168.1.301 | 1080p | Online |
| Warehouse CAM-W01 | IP | Storage Area 1 | 192.168.2.101 | 4K | Online |
| Loading Dock CAM-LD01 | IP | Loading Dock | 192.168.2.102 | 5MP | Online |
| Meeting Room CAM-M01 | IP | Meeting Room A | 192.168.1.401 | 4K | Offline |

**Camera Brands:** Mix of Hikvision, Dahua, and Axis cameras

### 5. Access Control Devices (4 total)

- Main Entry Card Reader (RFID/NFC)
- Executive Biometric Scanner (Fingerprint/Face/Card)
- IT Access Control (RFID/NFC/PIN)
- Parking Barrier Control (Auto-open/License Plate)

### 6. Environmental Sensors (5 total)

- Server Room Temperature Sensor (18-24°C)
- Server Room Humidity Sensor (40-60%)
- Warehouse Temperature Sensor (15-30°C)
- Lobby Motion Sensor
- Parking CO2 Sensor (< 1000 ppm)

### 7. Registered Persons (7 total)

| Name | Type | Department | Employee ID |
|------|------|------------|-------------|
| John Doe | Employee | Engineering | EMP001 |
| Jane Smith | Employee | HR | EMP002 |
| Mike Wilson | Employee | Security | EMP003 |
| Sarah Johnson | Employee | Finance | EMP004 |
| David Brown | Executive | Management | EXE001 |
| Lisa Chen | Contractor | IT Support | CNT001 |
| Robert Taylor | Visitor | - | - |

### 8. Automation Rules (5 total)

1. **After Hours Alert** - Motion detection after business hours
2. **Temperature Alert** - Server room temperature monitoring
3. **Unauthorized Access** - Alert on failed access attempts
4. **Parking Full Alert** - Notify when parking at 90% capacity
5. **Intrusion Detection** - High-priority security alert

### 9. Historical Data

- Sample events from the last 7 days
- Sample detections (persons, vehicles)
- Access logs
- Sensor readings

## 🔧 Advanced Usage

### Clear Existing Data Before Loading

```bash
# Python script with clear flag
python3 scripts/load_seed_data.py --clear

# Manual clear (use with caution!)
docker exec smartoffice-postgres psql -U smartoffice_user -d smartoffice -c "
TRUNCATE TABLE detections, events, automation_rules, registered_persons,
sensors, access_devices, cameras, zones, buildings, sites, users CASCADE;"
```

### Load to Different Database

```bash
# Python script
python3 scripts/load_seed_data.py \
  --host localhost \
  --port 5432 \
  --database custom_db \
  --user custom_user \
  --password custom_pass

# Bash script (using environment variables)
DB_NAME=custom_db DB_USER=custom_user ./scripts/load_seed_data.sh
```

### Verify Seed Data

```bash
# Check record counts
docker exec smartoffice-postgres psql -U smartoffice_user -d smartoffice -c "
SELECT
  'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'sites', COUNT(*) FROM sites
UNION ALL SELECT 'cameras', COUNT(*) FROM cameras
UNION ALL SELECT 'sensors', COUNT(*) FROM sensors;"
```

## 🎯 Use Cases

### For Testing

- **Authentication Testing**: Use different user roles (admin, security, operator, user)
- **Camera Testing**: Test with various camera types and statuses
- **Access Control**: Test card readers, biometric scanners
- **Alerts**: Trigger automation rules with sensor data
- **Multi-site**: Test across different locations and buildings

### For Development

- **UI Development**: Populate dashboards with realistic data
- **API Development**: Test endpoints with various data scenarios
- **Report Generation**: Generate analytics reports
- **Face Recognition**: Test with registered persons
- **Rule Engine**: Test automation triggers

### For Demos

- **Realistic Scenarios**: Show complete smart office setup
- **Multiple Sites**: Demonstrate multi-location management
- **Historical Data**: Show trends and patterns
- **Alerts & Notifications**: Demonstrate rule-based actions

## 📝 Customizing Seed Data

To customize the seed data for your needs:

1. **Edit `seed_data.sql`**:
   - Modify locations, addresses
   - Add/remove cameras
   - Change sensor thresholds
   - Add custom automation rules

2. **Add More Data**:
   - Add more users with different roles
   - Create additional zones
   - Add more registered persons
   - Increase historical events

3. **Adjust for Your Setup**:
   - Change IP addresses to match your network
   - Modify RTSP URLs for your cameras
   - Update timezones and coordinates
   - Customize department names

## ⚠️ Important Notes

### Security Considerations

1. **Change Default Passwords**: All users use `password123` - **CHANGE IN PRODUCTION**
2. **Secure Camera Credentials**: Default credentials are `admin` - update these
3. **API Keys**: No real API keys are included - add your own
4. **IP Addresses**: Sample IPs (192.168.x.x) - update for your network

### Database Prerequisites

1. **Run Migrations First**: Ensure all tables exist before loading seed data
   ```bash
   # Example with Alembic
   alembic upgrade head
   ```

2. **Extensions Required**:
   - `timescaledb` - For time-series data
   - `vector` - For face recognition embeddings
   - `uuid-ossp` - For UUID generation

3. **Permissions**: Database user needs INSERT permissions on all tables

### Troubleshooting

**Error: relation "users" does not exist**
- Run database migrations first to create tables

**Error: could not connect to database**
- Ensure PostgreSQL container is running
- Check database credentials

**Error: duplicate key value violates unique constraint**
- Data might already exist
- Use `--clear` flag to remove existing data

**Foreign Key Errors**
- Load seed_data.sql completely (it handles dependencies)
- Don't load partial SQL snippets

## 🔄 Updating Seed Data

To update seed data in an existing database:

```bash
# 1. Backup existing data
docker exec smartoffice-postgres pg_dump -U smartoffice_user smartoffice > backup.sql

# 2. Clear and reload
python3 scripts/load_seed_data.py --clear

# 3. Or manually update specific records
docker exec -i smartoffice-postgres psql -U smartoffice_user -d smartoffice
# Then run UPDATE/INSERT statements
```

## 📚 Related Documentation

- See `README.md` for service testing scripts
- See `init-db.sql` for database initialization
- See API documentation for data models

## 🤝 Contributing

To contribute additional seed data:

1. Follow the existing naming conventions
2. Ensure foreign key relationships are maintained
3. Add appropriate comments
4. Test loading on a fresh database
5. Update this README with new data descriptions

---

**Last Updated:** December 2024
**Database Schema Version:** Compatible with v1.0
