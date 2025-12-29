# Troubleshooting Guide

**Smart Office/Home Surveillance System**

Complete troubleshooting guide for common issues and solutions.

Version: 1.0.0
Last Updated: December 29, 2024

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [System Access Issues](#system-access-issues)
3. [Camera Problems](#camera-problems)
4. [Recording Issues](#recording-issues)
5. [Detection Problems](#detection-problems)
6. [Performance Issues](#performance-issues)
7. [Network & Connectivity](#network--connectivity)
8. [Database Issues](#database-issues)
9. [Service Failures](#service-failures)
10. [Common Error Messages](#common-error-messages)

---

## Quick Diagnosis

### System Health Check

Run these commands to quickly check system status:

```bash
# Check all services
docker-compose ps

# Check service logs
docker-compose logs --tail=100 auth-service

# Test database connection
docker exec smartoffice-postgres pg_isready -U smartoffice_user

# Test Redis
docker exec smartoffice-redis redis-cli ping

# Check disk space
df -h

# Check memory usage
free -h
```

### Health Check Script

```bash
#!/bin/bash
# Quick system health check

echo "=== System Health Check ==="

# Services
echo -n "PostgreSQL: "
docker exec smartoffice-postgres pg_isready -U smartoffice_user > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAIL"

echo -n "Redis: "
docker exec smartoffice-redis redis-cli ping > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAIL"

echo -n "Auth Service: "
curl -sf http://localhost:8001/health > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAIL"

echo -n "Data Service: "
curl -sf http://localhost:8002/health > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAIL"

# Resources
echo ""
echo "Disk Usage:"
df -h | grep -E "/$|/var"

echo ""
echo "Memory Usage:"
free -h | grep -E "Mem:|Swap:"

echo ""
echo "=== End Health Check ==="
```

---

## System Access Issues

### Cannot Login to Dashboard

**Symptom:** Login page shows but credentials don't work

**Possible Causes & Solutions:**

#### 1. Wrong Credentials
```bash
# Reset admin password
docker exec -it smartoffice-auth-service python <<EOF
from src.models.user import User
from src.core.database import SessionLocal
from src.core.security import hash_password

db = SessionLocal()
admin = db.query(User).filter(User.email == "admin@smartoffice.com").first()
admin.hashed_password = hash_password("newpassword123")
db.commit()
print("Password reset successful")
EOF
```

#### 2. Account Locked
```bash
# Unlock account
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice -c \
  "UPDATE users SET is_active = true, failed_login_attempts = 0 WHERE email = 'your.email@example.com';"
```

#### 3. Auth Service Down
```bash
# Check auth service
docker logs smartoffice-auth-service --tail=50

# Restart auth service
docker-compose restart auth-service

# Check if service is responding
curl http://localhost:8001/health
```

---

### Session Expires Immediately

**Symptom:** Login successful but immediately logged out

**Solutions:**

#### 1. Check JWT Configuration
```bash
# Verify JWT secret is set
docker exec smartoffice-auth-service env | grep JWT_SECRET_KEY

# If missing, add to .env
echo "JWT_SECRET_KEY=your-secret-key-here" >> .env

# Restart service
docker-compose restart auth-service
```

#### 2. Redis Connection Issues
```bash
# Test Redis
docker exec smartoffice-redis redis-cli ping
# Should return: PONG

# Check Redis logs
docker logs smartoffice-redis --tail=50

# Restart Redis
docker-compose restart redis
```

#### 3. Clock Synchronization
```bash
# Check system time
date

# Sync time (if incorrect)
sudo ntpdate -u time.nist.gov

# Or use systemd-timesyncd
sudo timedatectl set-ntp true
```

---

### "403 Forbidden" Error

**Symptom:** Access denied to certain pages or APIs

**Solutions:**

#### 1. Check User Permissions
```sql
-- Connect to database
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice

-- Check user role
SELECT email, role, is_active, is_superuser FROM users WHERE email = 'user@example.com';

-- Update role if needed
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
```

#### 2. CORS Issues (for API access)
```python
# services/auth-service/src/main.py

# Verify CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Add your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Camera Problems

### Camera Shows "Offline"

**Symptom:** Camera status shows red/offline indicator

**Diagnosis Steps:**

```bash
# 1. Ping camera
ping 192.168.1.100

# 2. Test RTSP stream directly
ffmpeg -i rtsp://192.168.1.100:554/stream1 -frames:v 1 test.jpg

# 3. Check camera credentials
# Use VLC Media Player: Media → Open Network Stream
# Enter: rtsp://username:password@192.168.1.100:554/stream1
```

**Solutions:**

#### 1. Network Connectivity
- Verify camera IP address
- Check network cables
- Ensure camera and server on same network/VLAN
- Check firewall rules

#### 2. Wrong Credentials
```bash
# Update camera credentials in database
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice -c \
  "UPDATE cameras SET username = 'admin', password = 'newpassword' WHERE name = 'Main Entrance';"
```

#### 3. Camera Rebooted
- Some cameras change IP after reboot
- Use static IP or DHCP reservation
- Update camera IP in system

#### 4. Bandwidth Limit
- Too many cameras streaming simultaneously
- Reduce resolution or frame rate
- Upgrade network infrastructure

---

### Poor Video Quality

**Symptom:** Blurry, pixelated, or choppy video

**Solutions:**

#### 1. Increase Resolution
```python
# Update camera settings via API
curl -X PUT http://localhost:8002/api/cameras/cam-001 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": "1920x1080",
    "frame_rate": 15,
    "bitrate": 2000
  }'
```

#### 2. Network Bandwidth
```bash
# Test network speed
iperf3 -c camera-ip-address

# Check for packet loss
ping -c 100 camera-ip-address | grep loss
```

#### 3. Camera Settings
- Clean camera lens
- Adjust exposure settings
- Enable WDR (Wide Dynamic Range) if backlit
- Adjust compression settings on camera

---

### Camera Keeps Disconnecting

**Symptom:** Camera goes offline and online repeatedly

**Solutions:**

#### 1. Power Issues
- Check PoE switch capacity
- Use dedicated power supply
- Verify voltage is stable

#### 2. Network Issues
- Replace network cable
- Check switch port
- Update camera firmware

#### 3. Resource Limits
```bash
# Check detection service resources
docker stats detection-service

# Increase resources in docker-compose.yml
services:
  detection-service:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

---

### Cannot Add New Camera

**Symptom:** Error when adding camera or camera not appearing

**Solutions:**

#### 1. Check RTSP URL Format
```
Correct formats:
rtsp://192.168.1.100:554/stream1
rtsp://username:password@192.168.1.100:554/stream1
rtsp://192.168.1.100/cam/realmonitor?channel=1&subtype=0
```

#### 2. Test Connection First
```bash
# Test with ffprobe
ffprobe -rtsp_transport tcp "rtsp://camera-url" 2>&1 | grep "Stream #"

# Should show video stream info
```

#### 3. Database Limits
```sql
-- Check camera count
SELECT COUNT(*) FROM cameras;

-- Check for license limit (if applicable)
-- Contact support to upgrade license
```

---

## Recording Issues

### Recordings Not Saving

**Symptom:** Live view works but no recordings found

**Diagnosis:**

```bash
# 1. Check storage space
df -h | grep minio
# or for local storage
df -h /var/lib/smartoffice/recordings

# 2. Check MinIO/S3
docker logs smartoffice-minio --tail=100

# 3. Check detection service logs
docker logs smartoffice-detection-service --tail=100 | grep -i record
```

**Solutions:**

#### 1. Storage Full
```bash
# Check storage usage
du -sh /var/lib/smartoffice/recordings/*

# Clean old recordings
find /var/lib/smartoffice/recordings -type f -mtime +30 -delete

# Or adjust retention policy
```

#### 2. MinIO Permission Issues
```bash
# Check MinIO status
curl http://localhost:9000/minio/health/live

# Verify bucket exists
docker exec smartoffice-minio mc ls minio/recordings

# Create bucket if missing
docker exec smartoffice-minio mc mb minio/recordings
```

#### 3. Recording Not Enabled
```sql
-- Check camera recording status
SELECT name, recording_enabled, recording_mode FROM cameras;

-- Enable recording
UPDATE cameras SET recording_enabled = true, recording_mode = 'continuous' WHERE id = 'cam-001';
```

---

### Cannot Play Recordings

**Symptom:** Recordings exist but won't play

**Solutions:**

#### 1. Codec Issues
```bash
# Check video codec
ffprobe /path/to/recording.mp4 2>&1 | grep "Video:"

# Convert to compatible format
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
```

#### 2. Corrupt File
```bash
# Try to repair
ffmpeg -i corrupt.mp4 -c copy repaired.mp4

# If still fails, recording may be lost
```

#### 3. Browser Compatibility
- Try different browser (Chrome recommended)
- Update browser to latest version
- Clear browser cache
- Disable browser extensions

---

### Recordings Have Gaps

**Symptom:** Missing segments in continuous recording

**Causes & Solutions:**

#### 1. Camera Disconnection
- See "Camera Keeps Disconnecting" section above

#### 2. Storage Issues
```bash
# Check for "disk full" errors in logs
docker logs smartoffice-detection-service | grep -i "disk\|space\|storage"

# Monitor disk usage
watch -n 5 'df -h'
```

#### 3. Service Restarts
```bash
# Check service uptime
docker ps | grep detection-service

# Check restart count
docker inspect smartoffice-detection-service | grep RestartCount
```

---

## Detection Problems

### No Person/Vehicle Detection

**Symptom:** Live feed works but no detection events

**Solutions:**

#### 1. Detection Not Enabled
```sql
-- Check detection settings
SELECT name, person_detection_enabled, vehicle_detection_enabled
FROM cameras
WHERE name = 'Your Camera';

-- Enable detection
UPDATE cameras
SET person_detection_enabled = true,
    vehicle_detection_enabled = true
WHERE name = 'Your Camera';
```

#### 2. Check Detection Service
```bash
# Check if detection service running
docker ps | grep detection-service

# Check logs for errors
docker logs smartoffice-detection-service --tail=100

# Restart detection service
docker-compose restart detection-service
```

#### 3. ML Model Issues
```bash
# Check if models loaded
docker logs smartoffice-detection-service | grep -i "model\|yolo"

# Should see: "YOLOv8 model loaded successfully"

# If missing, download models
docker exec smartoffice-detection-service python scripts/download_models.py
```

---

### Too Many False Detections

**Symptom:** Getting alerts for non-existent persons/vehicles

**Solutions:**

#### 1. Adjust Confidence Threshold
```python
# Increase minimum confidence
curl -X PUT http://localhost:8003/api/cameras/cam-001/detection-settings \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "min_confidence": 0.85,  # Increase from default 0.7
    "min_object_size": 100   # Ignore small objects
  }'
```

#### 2. Define Detection Zones
- Draw zones in camera settings
- Ignore areas with moving trees, flags, etc.
- Focus on areas of interest only

#### 3. Adjust Sensitivity
```
Low Sensitivity:    Fewer false alarms, may miss some real events
Medium Sensitivity: Balanced (recommended)
High Sensitivity:   Catch everything, more false alarms
```

---

### Face Recognition Not Working

**Symptom:** Persons detected but not identified

**Solutions:**

#### 1. Register Faces
```bash
# Check registered faces
curl http://localhost:8003/api/faces/registered \
  -H "Authorization: Bearer $TOKEN"

# Register new face
curl -X POST http://localhost:8003/api/faces/register \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@person_photo.jpg" \
  -F "name=John Doe" \
  -F "employee_id=EMP001"
```

#### 2. Face Quality
- Use clear, front-facing photos
- Good lighting
- No sunglasses or masks
- High resolution (min 200x200 pixels for face area)

#### 3. DeepFace Model
```bash
# Check DeepFace status
docker logs smartoffice-detection-service | grep -i deepface

# If errors, reinstall
docker exec smartoffice-detection-service pip install deepface --upgrade
```

---

## Performance Issues

### Slow Dashboard Loading

**Symptom:** Dashboard takes long time to load

**Solutions:**

#### 1. Clear Browser Cache
```
Chrome: Ctrl+Shift+Delete
Firefox: Ctrl+Shift+Delete
Safari: Cmd+Option+E
```

#### 2. Reduce Camera Grid
- Show fewer cameras simultaneously
- Use 2x2 instead of 4x4 grid
- Create camera groups

#### 3. Optimize Database
```sql
-- Connect to database
docker exec -it smartoffice-postgres psql -U smartoffice_user -d smartoffice

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM events ORDER BY timestamp DESC LIMIT 100;

-- Rebuild indexes
REINDEX TABLE events;

-- Vacuum database
VACUUM ANALYZE;
```

#### 4. Increase Redis Cache
```bash
# Edit docker-compose.yml
services:
  redis:
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

# Restart
docker-compose restart redis
```

---

### High CPU Usage

**Symptom:** System slow, high CPU usage

**Diagnosis:**

```bash
# Check CPU usage by service
docker stats

# Check processes
top
# or
htop
```

**Solutions:**

#### 1. Reduce Detection Frame Rate
```python
# Lower FPS for detection
curl -X PUT http://localhost:8003/api/cameras/cam-001/detection-settings \
  -d '{
    "detection_fps": 2  # Reduce from 5 to 2 FPS
  }'
```

#### 2. Disable Unused Features
- Disable face recognition if not needed
- Reduce number of active cameras
- Use motion-based detection instead of continuous

#### 3. Scale Resources
```yaml
# docker-compose.yml
services:
  detection-service:
    deploy:
      replicas: 2  # Add more instances
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

---

### High Memory Usage

**Symptom:** System runs out of memory

**Solutions:**

#### 1. Limit Service Memory
```yaml
# docker-compose.yml
services:
  detection-service:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

#### 2. Restart Services Periodically
```bash
# Add to crontab for weekly restart
0 3 * * 0 docker-compose restart detection-service
```

#### 3. Check for Memory Leaks
```bash
# Monitor memory over time
while true; do
  docker stats --no-stream detection-service >> memory.log
  sleep 60
done

# Analyze log
grep detection-service memory.log
```

---

## Network & Connectivity

### Cannot Access System Remotely

**Symptom:** Works on local network but not from internet

**Solutions:**

#### 1. Port Forwarding
```
Router Configuration:
External Port: 443
Internal IP: 192.168.1.100 (server IP)
Internal Port: 443
Protocol: TCP
```

#### 2. Firewall Rules
```bash
# Allow HTTPS
sudo ufw allow 443/tcp

# Allow HTTP (for redirect)
sudo ufw allow 80/tcp

# Check status
sudo ufw status
```

#### 3. Dynamic DNS
- Use service like DynDNS, No-IP
- Configure router to update IP
- Access via: https://yoursite.ddns.net

---

### Slow Video Streaming

**Symptom:** Laggy or buffering live feeds

**Solutions:**

#### 1. Network Bandwidth
```bash
# Test bandwidth
speedtest-cli

# Check network congestion
iftop  # or nethogs
```

#### 2. Reduce Stream Quality
```python
# Use substream instead of mainstream
curl -X PUT http://localhost:8002/api/cameras/cam-001 \
  -d '{
    "stream_profile": "substream",  # Lower quality
    "resolution": "1280x720"
  }'
```

#### 3. Use Transcoding
```yaml
# Add transcoding service
services:
  transcoder:
    image: jrottenberg/ffmpeg
    command: >
      -i rtsp://camera:554/stream1
      -c:v libx264 -preset ultrafast -tune zerolatency
      -f rtsp rtsp://localhost:8554/stream1_transcoded
```

---

## Database Issues

### Database Connection Failed

**Symptom:** Services can't connect to database

**Solutions:**

#### 1. Check PostgreSQL Status
```bash
# Is PostgreSQL running?
docker ps | grep postgres

# Check PostgreSQL logs
docker logs smartoffice-postgres --tail=50

# Restart PostgreSQL
docker-compose restart postgres
```

#### 2. Connection String
```bash
# Verify environment variables
docker exec smartoffice-auth-service env | grep DB_

# Should show:
# DB_HOST=postgres
# DB_PORT=5432
# DB_NAME=smartoffice
# DB_USER=smartoffice_user
# DB_PASSWORD=***
```

#### 3. Max Connections
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- Increase if needed
ALTER SYSTEM SET max_connections = 200;
-- Restart PostgreSQL
```

---

### Database Too Slow

**Symptom:** Queries taking long time

**Solutions:**

#### 1. Add Indexes
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_events_camera_time
ON events(camera_id, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_users_email
ON users(email);
```

#### 2. Optimize Configuration
```bash
# Edit postgresql.conf
docker exec smartoffice-postgres bash -c 'cat >> /var/lib/postgresql/data/postgresql.conf <<EOF
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 32MB
EOF'

# Restart
docker-compose restart postgres
```

#### 3. Partition Large Tables
```sql
-- Partition events table by month
CREATE TABLE events_2024_12 PARTITION OF events
FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE events_2025_01 PARTITION OF events
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## Service Failures

### Service Keeps Restarting

**Symptom:** Service restarts repeatedly

**Diagnosis:**

```bash
# Check restart count
docker ps -a | grep SERVICENAME

# View logs
docker logs --tail=200 smartoffice-SERVICENAME

# Check last exit code
docker inspect smartoffice-SERVICENAME | grep ExitCode
```

**Common Exit Codes:**

| Code | Meaning | Solution |
|------|---------|----------|
| 0 | Clean exit | Check why service stopped |
| 1 | General error | Check logs for details |
| 137 | Out of memory | Increase memory limit |
| 139 | Segmentation fault | Check dependencies, update libraries |

**Solutions:**

#### 1. Memory Issues (Exit Code 137)
```yaml
# Increase memory limit
services:
  service-name:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### 2. Missing Dependencies
```bash
# Reinstall dependencies
docker exec smartoffice-SERVICENAME pip install -r requirements.txt --force-reinstall
```

#### 3. Configuration Error
```bash
# Check environment variables
docker exec smartoffice-SERVICENAME env

# Validate configuration
docker exec smartoffice-SERVICENAME python -c "from src.core.config import settings; print('OK')"
```

---

### Service Won't Start

**Symptom:** Service fails to start

**Solutions:**

#### 1. Check Dependencies
```bash
# Ensure database is ready
docker-compose up -d postgres
sleep 10  # Wait for PostgreSQL to be ready

# Then start service
docker-compose up -d auth-service
```

#### 2. Port Conflict
```bash
# Check if port in use
lsof -i :8001

# Kill conflicting process
kill -9 <PID>

# Or change port in docker-compose.yml
```

#### 3. Build Errors
```bash
# Rebuild image
docker-compose build --no-cache auth-service

# Check build logs
docker-compose build auth-service 2>&1 | tee build.log
```

---

## Common Error Messages

### "ECONNREFUSED" or "Connection refused"

**Meaning:** Cannot connect to service

**Solutions:**
1. Check if service is running
2. Verify port number
3. Check firewall rules
4. Ensure service finished starting

---

### "401 Unauthorized"

**Meaning:** Authentication failed

**Solutions:**
1. Check if logged in
2. Verify token is valid (not expired)
3. Ensure Authorization header is set
4. Check user permissions

---

### "500 Internal Server Error"

**Meaning:** Server-side error

**Solutions:**
1. Check service logs
2. Look for stack traces
3. Verify database connection
4. Check for missing environment variables

---

### "CORS Error" in Browser

**Meaning:** Cross-origin request blocked

**Solutions:**
```python
# Add domain to CORS whitelist
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "http://localhost:3000"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### "Disk quota exceeded"

**Meaning:** Out of storage space

**Solutions:**
```bash
# Check disk usage
df -h

# Find large files
du -h / | sort -rh | head -20

# Clean old recordings
find /var/lib/smartoffice/recordings -mtime +30 -delete

# Clean Docker
docker system prune -a
```

---

## Getting Additional Help

### Collecting Diagnostic Information

```bash
#!/bin/bash
# Generate diagnostic report

REPORT_FILE="diagnostic-report-$(date +%Y%m%d-%H%M%S).txt"

echo "=== System Diagnostic Report ===" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

echo "=== Docker Services ===" >> $REPORT_FILE
docker-compose ps >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "=== Service Logs ===" >> $REPORT_FILE
docker-compose logs --tail=50 >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "=== System Resources ===" >> $REPORT_FILE
df -h >> $REPORT_FILE
free -h >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "=== Network ===" >> $REPORT_FILE
ifconfig >> $REPORT_FILE

echo "Report saved to: $REPORT_FILE"
```

### Contacting Support

When contacting support, include:
1. Diagnostic report (above)
2. Steps to reproduce the issue
3. Error messages or screenshots
4. System version
5. When issue started

**Support Channels:**
- Email: support@example.com
- Phone: 1-800-XXX-XXXX
- Support Portal: https://support.example.com
- Emergency: +1-XXX-XXX-XXXX (24/7)

---

## Preventive Maintenance

### Daily Checks
- ✅ Verify all cameras online
- ✅ Check recent events
- ✅ Review system health dashboard

### Weekly Maintenance
- ✅ Review storage usage
- ✅ Check service logs for errors
- ✅ Test backup restore
- ✅ Review user access logs

### Monthly Maintenance
- ✅ Update system software
- ✅ Clean old recordings
- ✅ Review and optimize rules
- ✅ Performance analysis
- ✅ Security audit

---

**Remember:** Most issues can be resolved by checking logs, restarting services, or verifying configuration. When in doubt, consult this guide or contact support!
