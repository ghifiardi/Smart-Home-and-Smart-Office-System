-- Smart Office Surveillance System - Seed Data
-- This file contains sample data for testing and development

-- =============================================================================
-- 1. USERS AND AUTHENTICATION
-- =============================================================================

-- Sample Users (passwords are hashed with bcrypt - all use 'password123' as plain text)
-- Hash generated with: bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())

INSERT INTO users (id, email, username, hashed_password, full_name, is_active, is_superuser, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'admin@smartoffice.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'System Administrator', true, true, NOW(), NOW()),
    (uuid_generate_v4(), 'security@smartoffice.com', 'security_manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'Security Manager', true, false, NOW(), NOW()),
    (uuid_generate_v4(), 'operator@smartoffice.com', 'operator1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'Control Room Operator', true, false, NOW(), NOW()),
    (uuid_generate_v4(), 'john.doe@smartoffice.com', 'johndoe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'John Doe', true, false, NOW(), NOW()),
    (uuid_generate_v4(), 'jane.smith@smartoffice.com', 'janesmith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'Jane Smith', true, false, NOW(), NOW()),
    (uuid_generate_v4(), 'mike.wilson@smartoffice.com', 'mikewilson', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'Mike Wilson', true, false, NOW(), NOW()),
    (uuid_generate_v4(), 'guest@smartoffice.com', 'guest', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNGz8jN.u', 'Guest User', true, false, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- =============================================================================
-- 2. SITES AND LOCATIONS
-- =============================================================================

-- Main Headquarters
INSERT INTO sites (id, name, address, city, country, postal_code, timezone, latitude, longitude, is_active, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'HQ Building - Jakarta', 'Jl. Sudirman No. 123', 'Jakarta', 'Indonesia', '12190', 'Asia/Jakarta', -6.2088, 106.8456, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Branch Office - Surabaya', 'Jl. Basuki Rahmat No. 45', 'Surabaya', 'Indonesia', '60271', 'Asia/Jakarta', -7.2575, 112.7521, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Branch Office - Bandung', 'Jl. Asia Afrika No. 78', 'Bandung', 'Indonesia', '40111', 'Asia/Jakarta', -6.9175, 107.6191, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Warehouse - Tangerang', 'Jl. Raya Serpong No. 99', 'Tangerang', 'Indonesia', '15310', 'Asia/Jakarta', -6.2382, 106.6322, true, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Buildings within sites
INSERT INTO buildings (id, site_id, name, floors, description, created_at, updated_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM sites WHERE name = 'HQ Building - Jakarta' LIMIT 1), 'Main Tower', 20, 'Main office building with executive offices', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM sites WHERE name = 'HQ Building - Jakarta' LIMIT 1), 'Annex Building', 5, 'Additional office space and meeting rooms', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM sites WHERE name = 'Branch Office - Surabaya' LIMIT 1), 'Office Block A', 8, 'Primary office building', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM sites WHERE name = 'Warehouse - Tangerang' LIMIT 1), 'Storage Facility 1', 1, 'Main storage warehouse', NOW(), NOW())
ON CONFLICT (site_id, name) DO NOTHING;

-- Zones within buildings
INSERT INTO zones (id, building_id, name, floor_number, zone_type, description, created_at, updated_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'Main Lobby', 1, 'public', 'Main entrance and reception area', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'Executive Floor', 20, 'restricted', 'C-level executive offices', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'IT Department', 5, 'restricted', 'Information Technology department', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'Meeting Room A', 10, 'restricted', 'Large conference room', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'Cafeteria', 1, 'public', 'Employee dining area', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Main Tower' LIMIT 1), 'Parking Basement', -1, 'public', 'Underground parking facility', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Annex Building' LIMIT 1), 'Training Room', 2, 'restricted', 'Employee training and development', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Storage Facility 1' LIMIT 1), 'Storage Area 1', 1, 'restricted', 'Primary storage zone', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM buildings WHERE name = 'Storage Facility 1' LIMIT 1), 'Loading Dock', 1, 'restricted', 'Loading and unloading area', NOW(), NOW())
ON CONFLICT (building_id, name) DO NOTHING;

-- =============================================================================
-- 3. CAMERAS AND SURVEILLANCE DEVICES
-- =============================================================================

-- IP Cameras
INSERT INTO cameras (id, zone_id, name, camera_type, model, ip_address, rtsp_url, username, status, position, field_of_view, resolution, fps, is_active, created_at, updated_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), 'Lobby Entrance CAM-001', 'ip', 'Hikvision DS-2CD2385G1', '192.168.1.101', 'rtsp://192.168.1.101:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 3}', 110, '3840x2160', 30, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), 'Lobby Reception CAM-002', 'ip', 'Hikvision DS-2CD2385G1', '192.168.1.102', 'rtsp://192.168.1.102:554/stream1', 'admin', 'online', '{"x": 5, "y": 0, "z": 3}', 110, '3840x2160', 30, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Executive Floor' LIMIT 1), 'Executive Hallway CAM-201', 'ptz', 'Hikvision DS-2DE4425IW-DE', '192.168.1.201', 'rtsp://192.168.1.201:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 2.5}', 360, '1920x1080', 25, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'IT Department' LIMIT 1), 'IT Server Room CAM-501', 'ip', 'Dahua IPC-HFW5541E-ZE', '192.168.1.501', 'rtsp://192.168.1.501:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 2.8}', 90, '2592x1944', 30, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), 'Parking Entry CAM-B01', 'ip', 'Hikvision DS-2CD2T85G1', '192.168.1.151', 'rtsp://192.168.1.151:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 2.5}', 110, '3840x2160', 25, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), 'Parking Exit CAM-B02', 'ip', 'Hikvision DS-2CD2T85G1', '192.168.1.152', 'rtsp://192.168.1.152:554/stream1', 'admin', 'online', '{"x": 20, "y": 0, "z": 2.5}', 110, '3840x2160', 25, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Cafeteria' LIMIT 1), 'Cafeteria Main CAM-C01', 'ip', 'Axis P3245-LVE', '192.168.1.301', 'rtsp://192.168.1.301:554/stream1', 'admin', 'online', '{"x": 10, "y": 0, "z": 3}', 120, '1920x1080', 30, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Storage Area 1' LIMIT 1), 'Warehouse CAM-W01', 'ip', 'Hikvision DS-2CD2385G1', '192.168.2.101', 'rtsp://192.168.2.101:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 4}', 110, '3840x2160', 20, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Loading Dock' LIMIT 1), 'Loading Dock CAM-LD01', 'ip', 'Dahua IPC-HFW5541E-ZE', '192.168.2.102', 'rtsp://192.168.2.102:554/stream1', 'admin', 'online', '{"x": 0, "y": 0, "z": 3.5}', 90, '2592x1944', 20, true, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Meeting Room A' LIMIT 1), 'Meeting Room CAM-M01', 'ip', 'Hikvision DS-2CD2385G1', '192.168.1.401', 'rtsp://192.168.1.401:554/stream1', 'admin', 'offline', '{"x": 0, "y": 0, "z": 2.5}', 110, '3840x2160', 30, true, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 4. IoT SENSORS AND DEVICES
-- =============================================================================

-- Access Control Devices
INSERT INTO access_devices (id, zone_id, device_name, device_type, mac_address, ip_address, protocol, status, capabilities, created_at, updated_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), 'Main Entry Card Reader', 'card_reader', '00:1B:44:11:3A:B7', '192.168.1.50', 'wiegand', 'online', '{"rfid": true, "nfc": true, "pin": false}', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Executive Floor' LIMIT 1), 'Executive Biometric Scanner', 'biometric', '00:1B:44:11:3A:B8', '192.168.1.51', 'tcp', 'online', '{"fingerprint": true, "face": true, "card": true}', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'IT Department' LIMIT 1), 'IT Access Control', 'card_reader', '00:1B:44:11:3A:B9', '192.168.1.52', 'wiegand', 'online', '{"rfid": true, "nfc": true, "pin": true}', NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), 'Parking Barrier Control', 'barrier', '00:1B:44:11:3A:BA', '192.168.1.53', 'mqtt', 'online', '{"auto_open": true, "license_plate": true}', NOW(), NOW())
ON CONFLICT (device_name) DO NOTHING;

-- Environmental Sensors
INSERT INTO sensors (id, zone_id, sensor_name, sensor_type, mac_address, protocol, status, unit, threshold_min, threshold_max, created_at, updated_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'IT Department' LIMIT 1), 'Server Room Temp Sensor', 'temperature', '00:1B:44:22:3A:C1', 'mqtt', 'online', 'celsius', 18.0, 24.0, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'IT Department' LIMIT 1), 'Server Room Humidity Sensor', 'humidity', '00:1B:44:22:3A:C2', 'mqtt', 'online', 'percent', 40.0, 60.0, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Storage Area 1' LIMIT 1), 'Warehouse Temp Sensor', 'temperature', '00:1B:44:22:3A:C3', 'mqtt', 'online', 'celsius', 15.0, 30.0, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), 'Lobby Motion Sensor', 'motion', '00:1B:44:22:3A:C4', 'mqtt', 'online', 'boolean', NULL, NULL, NOW(), NOW()),
    (uuid_generate_v4(), (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), 'Parking CO2 Sensor', 'air_quality', '00:1B:44:22:3A:C5', 'mqtt', 'online', 'ppm', NULL, 1000.0, NOW(), NOW())
ON CONFLICT (sensor_name) DO NOTHING;

-- =============================================================================
-- 5. REGISTERED PERSONS (FOR FACE RECOGNITION)
-- =============================================================================

INSERT INTO registered_persons (id, full_name, person_type, department, employee_id, email, phone, face_encoding, is_active, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'John Doe', 'employee', 'Engineering', 'EMP001', 'john.doe@smartoffice.com', '+62-812-3456-7890', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Jane Smith', 'employee', 'HR', 'EMP002', 'jane.smith@smartoffice.com', '+62-812-3456-7891', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Mike Wilson', 'employee', 'Security', 'EMP003', 'mike.wilson@smartoffice.com', '+62-812-3456-7892', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Sarah Johnson', 'employee', 'Finance', 'EMP004', 'sarah.johnson@smartoffice.com', '+62-812-3456-7893', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'David Brown', 'executive', 'Management', 'EXE001', 'david.brown@smartoffice.com', '+62-812-3456-7894', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Lisa Chen', 'contractor', 'IT Support', 'CNT001', 'lisa.chen@contractor.com', '+62-812-3456-7895', NULL, true, NOW(), NOW()),
    (uuid_generate_v4(), 'Robert Taylor', 'visitor', NULL, NULL, NULL, NULL, NULL, true, NOW(), NOW())
ON CONFLICT (employee_id) DO NOTHING;

-- =============================================================================
-- 6. AUTOMATION RULES
-- =============================================================================

INSERT INTO automation_rules (id, name, description, rule_type, trigger_type, conditions, actions, is_active, priority, created_at, updated_at) VALUES
    (uuid_generate_v4(),
     'After Hours Alert',
     'Send alert when motion detected after business hours',
     'security',
     'motion_detected',
     '{"time_range": {"start": "18:00", "end": "06:00"}, "zones": ["Executive Floor", "IT Department"]}',
     '{"notifications": [{"type": "email", "recipients": ["security@smartoffice.com"]}, {"type": "sms", "recipients": ["+62-812-SECURITY"]}]}',
     true,
     1,
     NOW(), NOW()),

    (uuid_generate_v4(),
     'Temperature Alert',
     'Alert when server room temperature exceeds threshold',
     'environmental',
     'sensor_threshold',
     '{"sensor_type": "temperature", "threshold": 26.0, "comparison": "greater_than", "zones": ["IT Department"]}',
     '{"notifications": [{"type": "email", "recipients": ["it@smartoffice.com"]}], "actions": [{"type": "hvac_adjust", "target_temp": 22.0}]}',
     true,
     2,
     NOW(), NOW()),

    (uuid_generate_v4(),
     'Unauthorized Access',
     'Alert on access attempt without valid credentials',
     'security',
     'access_denied',
     '{"zones": ["Executive Floor", "IT Department"], "consecutive_attempts": 3}',
     '{"notifications": [{"type": "email", "recipients": ["security@smartoffice.com"]}, {"type": "push", "recipients": ["security_team"]}], "actions": [{"type": "camera_record", "duration": 300}]}',
     true,
     1,
     NOW(), NOW()),

    (uuid_generate_v4(),
     'Parking Full Alert',
     'Notify when parking occupancy exceeds 90%',
     'operational',
     'threshold',
     '{"metric": "parking_occupancy", "threshold": 90, "comparison": "greater_than"}',
     '{"notifications": [{"type": "display", "location": "parking_entrance", "message": "Parking Full - Please Use Alternative Parking"}]}',
     true,
     3,
     NOW(), NOW()),

    (uuid_generate_v4(),
     'Intrusion Detection',
     'High priority alert for detected intrusion',
     'security',
     'object_detected',
     '{"object_class": "person", "time_range": {"start": "22:00", "end": "05:00"}, "zones": ["Storage Area 1", "Loading Dock"], "confidence_threshold": 0.85}',
     '{"notifications": [{"type": "email", "recipients": ["security@smartoffice.com"]}, {"type": "sms", "recipients": ["+62-812-SECURITY"]}, {"type": "alarm", "level": "high"}], "actions": [{"type": "camera_record_all", "duration": 600}, {"type": "lock_zone"}]}',
     true,
     1,
     NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- 7. SAMPLE HISTORICAL DATA (EVENTS AND DETECTIONS)
-- =============================================================================

-- Sample Events (last 7 days)
INSERT INTO events (id, event_type, severity, zone_id, camera_id, description, metadata, timestamp, created_at) VALUES
    (uuid_generate_v4(), 'access_granted', 'info', (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), NULL, 'Access granted to John Doe', '{"person": "John Doe", "method": "card"}', NOW() - INTERVAL '1 hour', NOW()),
    (uuid_generate_v4(), 'motion_detected', 'warning', (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), (SELECT id FROM cameras WHERE name LIKE 'Parking%' LIMIT 1), 'Motion detected in parking area', '{"confidence": 0.92}', NOW() - INTERVAL '2 hours', NOW()),
    (uuid_generate_v4(), 'person_detected', 'info', (SELECT id FROM zones WHERE name = 'Cafeteria' LIMIT 1), (SELECT id FROM cameras WHERE name LIKE 'Cafeteria%' LIMIT 1), 'Person detected in cafeteria', '{"count": 15, "confidence": 0.89}', NOW() - INTERVAL '3 hours', NOW()),
    (uuid_generate_v4(), 'temperature_alert', 'warning', (SELECT id FROM zones WHERE name = 'IT Department' LIMIT 1), NULL, 'Server room temperature above threshold', '{"temperature": 26.5, "threshold": 24.0}', NOW() - INTERVAL '1 day', NOW()),
    (uuid_generate_v4(), 'access_denied', 'warning', (SELECT id FROM zones WHERE name = 'Executive Floor' LIMIT 1), NULL, 'Access denied - invalid card', '{"card_id": "unknown"}', NOW() - INTERVAL '2 days', NOW())
ON CONFLICT DO NOTHING;

-- Sample Detections
INSERT INTO detections (id, camera_id, zone_id, object_class, confidence, bounding_box, track_id, timestamp, created_at) VALUES
    (uuid_generate_v4(), (SELECT id FROM cameras WHERE name LIKE 'Lobby%' LIMIT 1), (SELECT id FROM zones WHERE name = 'Main Lobby' LIMIT 1), 'person', 0.95, '{"x": 100, "y": 150, "width": 80, "height": 200}', 'track_001', NOW() - INTERVAL '30 minutes', NOW()),
    (uuid_generate_v4(), (SELECT id FROM cameras WHERE name LIKE 'Parking%' LIMIT 1), (SELECT id FROM zones WHERE name = 'Parking Basement' LIMIT 1), 'car', 0.92, '{"x": 200, "y": 180, "width": 150, "height": 120}', 'track_002', NOW() - INTERVAL '1 hour', NOW()),
    (uuid_generate_v4(), (SELECT id FROM cameras WHERE name LIKE 'Cafeteria%' LIMIT 1), (SELECT id FROM zones WHERE name = 'Cafeteria' LIMIT 1), 'person', 0.88, '{"x": 300, "y": 200, "width": 70, "height": 190}', 'track_003', NOW() - INTERVAL '2 hours', NOW())
ON CONFLICT DO NOTHING;

-- =============================================================================
-- SUMMARY
-- =============================================================================
-- Total seed data created:
-- - 7 Users (including 1 admin, 1 security manager, 1 operator, 4 regular users)
-- - 4 Sites (Jakarta HQ, Surabaya, Bandung, Tangerang warehouse)
-- - 4 Buildings
-- - 9 Zones
-- - 10 Cameras (mix of IP and PTZ cameras)
-- - 4 Access Control Devices
-- - 5 Environmental Sensors
-- - 7 Registered Persons (for face recognition)
-- - 5 Automation Rules
-- - Sample historical events and detections
-- =============================================================================

-- Print summary
DO $$
BEGIN
    RAISE NOTICE 'Seed data loaded successfully!';
    RAISE NOTICE 'Default login credentials:';
    RAISE NOTICE '  Admin: admin@smartoffice.com / password123';
    RAISE NOTICE '  Security: security@smartoffice.com / password123';
    RAISE NOTICE '  Operator: operator@smartoffice.com / password123';
END $$;
