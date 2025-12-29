# API Reference

**Smart Office/Home Surveillance System - REST API Documentation**

Version: 1.0.0
Last Updated: December 29, 2024
Base URL: `https://your-domain.com/api`

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Camera Management](#camera-management)
4. [Detection & Events](#detection--events)
5. [Access Control](#access-control)
6. [Automation Rules](#automation-rules)
7. [Notifications](#notifications)
8. [Analytics](#analytics)
9. [System](#system)
10. [Error Codes](#error-codes)

---

## Authentication

### Login

Authenticate user and receive JWT token.

**Endpoint:** `POST /auth/login`

**Request:**
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

---

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Request:**
```http
POST /api/auth/register
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "role": "user",
  "created_at": "2024-12-29T10:00:00Z"
}
```

**Status Codes:**
- `201 Created` - User created successfully
- `400 Bad Request` - Invalid input
- `409 Conflict` - Email or username already exists

---

### Get Current User

Get authenticated user's profile.

**Endpoint:** `GET /auth/me`

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "role": "user",
  "created_at": "2024-12-29T10:00:00Z",
  "last_login": "2024-12-29T15:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Invalid or expired token

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### Logout

Invalidate current token.

**Endpoint:** `POST /auth/logout`

**Headers:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Status Codes:**
- `200 OK` - Logout successful

---

## User Management

### List Users

Get list of users (Admin only).

**Endpoint:** `GET /users`

**Parameters:**
- `skip` (integer) - Number of records to skip (pagination)
- `limit` (integer) - Maximum records to return (max: 100)
- `role` (string) - Filter by role
- `is_active` (boolean) - Filter by active status

**Example:**
```http
GET /api/users?skip=0&limit=20&role=user&is_active=true
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 20,
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "user",
      "is_active": true,
      "created_at": "2024-12-29T10:00:00Z"
    }
  ]
}
```

---

### Update User

Update user details (Own profile or Admin).

**Endpoint:** `PUT /users/{user_id}`

**Request:**
```json
{
  "full_name": "John Smith",
  "role": "admin"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Smith",
  "role": "admin",
  "updated_at": "2024-12-29T16:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Update successful
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - User not found

---

## Camera Management

### List Cameras

Get all cameras accessible to the user.

**Endpoint:** `GET /cameras`

**Parameters:**
- `skip` (integer) - Pagination offset
- `limit` (integer) - Max results (default: 50)
- `zone_id` (UUID) - Filter by zone
- `status` (string) - Filter by status: online, offline, disabled

**Example:**
```http
GET /api/cameras?limit=10&status=online
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "total": 45,
  "cameras": [
    {
      "id": "cam-001",
      "name": "Main Entrance",
      "location": "Building A - Floor 1",
      "zone_id": "zone-123",
      "stream_url": "rtsp://192.168.1.100:554/stream1",
      "status": "online",
      "resolution": "1920x1080",
      "frame_rate": 15,
      "recording_enabled": true,
      "person_detection_enabled": true,
      "vehicle_detection_enabled": true,
      "is_active": true,
      "created_at": "2024-12-01T00:00:00Z",
      "last_seen": "2024-12-29T16:00:00Z"
    }
  ]
}
```

---

### Get Camera Details

Get detailed information about a specific camera.

**Endpoint:** `GET /cameras/{camera_id}`

**Response:**
```json
{
  "id": "cam-001",
  "name": "Main Entrance",
  "location": "Building A - Floor 1",
  "zone": {
    "id": "zone-123",
    "name": "Main Entrance Zone",
    "site": {
      "id": "site-001",
      "name": "HQ Building - Jakarta"
    }
  },
  "stream_url": "rtsp://192.168.1.100:554/stream1",
  "status": "online",
  "resolution": "1920x1080",
  "frame_rate": 15,
  "recording_enabled": true,
  "recording_mode": "continuous",
  "detection_settings": {
    "person_detection_enabled": true,
    "vehicle_detection_enabled": true,
    "face_recognition_enabled": true,
    "min_confidence": 0.75,
    "detection_fps": 5
  },
  "is_active": true,
  "created_at": "2024-12-01T00:00:00Z",
  "updated_at": "2024-12-29T12:00:00Z",
  "last_seen": "2024-12-29T16:00:00Z"
}
```

---

### Create Camera

Register a new camera.

**Endpoint:** `POST /cameras`

**Request:**
```json
{
  "name": "Parking Lot Camera 1",
  "location": "Building A - Parking",
  "zone_id": "zone-456",
  "stream_url": "rtsp://192.168.1.101:554/stream1",
  "username": "admin",
  "password": "camera_password",
  "resolution": "1920x1080",
  "frame_rate": 15,
  "recording_enabled": true,
  "recording_mode": "motion",
  "person_detection_enabled": true,
  "vehicle_detection_enabled": true
}
```

**Response:**
```json
{
  "id": "cam-002",
  "name": "Parking Lot Camera 1",
  "status": "testing",
  "message": "Camera created. Testing connection..."
}
```

**Status Codes:**
- `201 Created` - Camera created successfully
- `400 Bad Request` - Invalid camera configuration
- `409 Conflict` - Camera with same stream URL exists

---

### Update Camera

Update camera configuration.

**Endpoint:** `PUT /cameras/{camera_id}`

**Request:**
```json
{
  "name": "Updated Camera Name",
  "recording_enabled": false,
  "person_detection_enabled": true,
  "min_confidence": 0.85
}
```

**Response:**
```json
{
  "id": "cam-001",
  "name": "Updated Camera Name",
  "recording_enabled": false,
  "updated_at": "2024-12-29T16:30:00Z"
}
```

---

### Delete Camera

Remove a camera from the system.

**Endpoint:** `DELETE /cameras/{camera_id}`

**Response:**
```json
{
  "message": "Camera deleted successfully"
}
```

**Status Codes:**
- `200 OK` - Camera deleted
- `404 Not Found` - Camera not found

---

### Start/Stop Recording

Control camera recording manually.

**Endpoint:** `POST /cameras/{camera_id}/recording/{action}`

**Parameters:**
- `action`: `start` or `stop`

**Example:**
```http
POST /api/cameras/cam-001/recording/start
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "camera_id": "cam-001",
  "recording": true,
  "message": "Recording started"
}
```

---

## Detection & Events

### Get Recent Events

Get recent detection events.

**Endpoint:** `GET /events`

**Parameters:**
- `skip` (integer) - Pagination offset
- `limit` (integer) - Max results (default: 50, max: 100)
- `camera_id` (string) - Filter by camera
- `event_type` (string) - Filter by type: person, vehicle, motion, face
- `start_time` (datetime) - Start of time range
- `end_time` (datetime) - End of time range
- `min_confidence` (float) - Minimum detection confidence (0.0-1.0)

**Example:**
```http
GET /api/events?camera_id=cam-001&event_type=person&limit=20
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "total": 1250,
  "events": [
    {
      "id": "evt-12345",
      "event_type": "person",
      "camera_id": "cam-001",
      "camera_name": "Main Entrance",
      "timestamp": "2024-12-29T16:45:30Z",
      "confidence": 0.95,
      "thumbnail_url": "https://storage.example.com/thumbnails/evt-12345.jpg",
      "video_url": "https://storage.example.com/clips/evt-12345.mp4",
      "metadata": {
        "person_count": 1,
        "bounding_boxes": [
          {
            "x": 150,
            "y": 200,
            "width": 100,
            "height": 300,
            "confidence": 0.95
          }
        ],
        "face_recognized": false
      }
    }
  ]
}
```

---

### Get Event Details

Get detailed information about a specific event.

**Endpoint:** `GET /events/{event_id}`

**Response:**
```json
{
  "id": "evt-12345",
  "event_type": "person",
  "camera": {
    "id": "cam-001",
    "name": "Main Entrance",
    "location": "Building A - Floor 1"
  },
  "timestamp": "2024-12-29T16:45:30Z",
  "confidence": 0.95,
  "duration": 5.2,
  "thumbnail_url": "https://storage.example.com/thumbnails/evt-12345.jpg",
  "video_url": "https://storage.example.com/clips/evt-12345.mp4",
  "full_resolution_url": "https://storage.example.com/full/evt-12345.jpg",
  "metadata": {
    "person_count": 1,
    "bounding_boxes": [
      {
        "x": 150,
        "y": 200,
        "width": 100,
        "height": 300,
        "confidence": 0.95,
        "class": "person"
      }
    ],
    "face_recognized": true,
    "person": {
      "id": "person-789",
      "name": "John Doe",
      "confidence": 0.88
    },
    "rules_triggered": ["after-hours-alert"]
  },
  "created_at": "2024-12-29T16:45:30Z"
}
```

---

### Export Event Clip

Export video clip for an event.

**Endpoint:** `POST /events/{event_id}/export`

**Request:**
```json
{
  "format": "mp4",
  "resolution": "1920x1080",
  "include_audio": true,
  "add_watermark": true
}
```

**Response:**
```json
{
  "export_id": "export-456",
  "status": "processing",
  "estimated_completion": "2024-12-29T17:00:00Z"
}
```

---

### Delete Event

Delete an event and associated media.

**Endpoint:** `DELETE /events/{event_id}`

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

---

## Access Control

### List Access Devices

Get all access control devices.

**Endpoint:** `GET /access/devices`

**Response:**
```json
{
  "total": 12,
  "devices": [
    {
      "id": "device-001",
      "name": "Main Entrance Door",
      "type": "door_lock",
      "location": "Building A - Main Entrance",
      "zone_id": "zone-123",
      "status": "online",
      "is_locked": true,
      "access_mode": "card_pin",
      "last_access": "2024-12-29T16:30:00Z",
      "created_at": "2024-12-01T00:00:00Z"
    }
  ]
}
```

---

### Control Device

Lock/unlock device remotely.

**Endpoint:** `POST /access/devices/{device_id}/control`

**Request:**
```json
{
  "action": "unlock",
  "duration": 5
}
```

**Parameters:**
- `action`: `lock` or `unlock`
- `duration` (optional): Seconds to keep unlocked (default: 5)

**Response:**
```json
{
  "device_id": "device-001",
  "action": "unlock",
  "status": "success",
  "timestamp": "2024-12-29T17:00:00Z",
  "auto_lock_at": "2024-12-29T17:00:05Z"
}
```

---

### Get Access Log

Get access event log.

**Endpoint:** `GET /access/log`

**Parameters:**
- `device_id` (string) - Filter by device
- `user_id` (string) - Filter by user
- `start_time` (datetime) - Start of time range
- `end_time` (datetime) - End of time range
- `status` (string) - Filter by status: granted, denied
- `skip` (integer) - Pagination
- `limit` (integer) - Max results

**Response:**
```json
{
  "total": 5420,
  "events": [
    {
      "id": "access-001",
      "device_id": "device-001",
      "device_name": "Main Entrance Door",
      "user_id": "user-123",
      "user_name": "John Doe",
      "card_number": "12345678",
      "status": "granted",
      "method": "card",
      "timestamp": "2024-12-29T17:00:00Z",
      "denied_reason": null
    },
    {
      "id": "access-002",
      "device_id": "device-001",
      "device_name": "Main Entrance Door",
      "user_id": null,
      "card_number": "87654321",
      "status": "denied",
      "method": "card",
      "timestamp": "2024-12-29T17:05:00Z",
      "denied_reason": "Invalid card"
    }
  ]
}
```

---

### Register Access Card

Register a new access card.

**Endpoint:** `POST /access/cards`

**Request:**
```json
{
  "card_number": "12345678",
  "user_id": "user-123",
  "access_level": "employee",
  "valid_from": "2024-12-29T00:00:00Z",
  "valid_until": "2025-12-31T23:59:59Z",
  "enabled": true
}
```

**Response:**
```json
{
  "id": "card-001",
  "card_number": "12345678",
  "user_id": "user-123",
  "access_level": "employee",
  "valid_from": "2024-12-29T00:00:00Z",
  "valid_until": "2025-12-31T23:59:59Z",
  "enabled": true,
  "created_at": "2024-12-29T17:10:00Z"
}
```

---

## Automation Rules

### List Rules

Get all automation rules.

**Endpoint:** `GET /rules`

**Response:**
```json
{
  "total": 15,
  "rules": [
    {
      "id": "rule-001",
      "name": "After Hours Alert",
      "description": "Alert security when person detected after hours",
      "trigger_type": "event",
      "trigger_config": {
        "event_type": "person"
      },
      "conditions": [
        {
          "type": "time_range",
          "start_time": "18:00",
          "end_time": "06:00"
        },
        {
          "type": "zone",
          "zones": ["zone-123", "zone-456"]
        },
        {
          "type": "confidence",
          "min_confidence": 0.80
        }
      ],
      "actions": [
        {
          "type": "notification",
          "channels": ["push", "email"],
          "recipients": ["security-team"]
        },
        {
          "type": "recording",
          "cameras": ["all_nearby"],
          "duration": 300
        }
      ],
      "enabled": true,
      "priority": "high",
      "created_at": "2024-12-15T00:00:00Z",
      "last_triggered": "2024-12-29T02:30:00Z",
      "trigger_count": 45
    }
  ]
}
```

---

### Create Rule

Create a new automation rule.

**Endpoint:** `POST /rules`

**Request:**
```json
{
  "name": "Temperature Alert",
  "description": "Alert when server room temperature exceeds threshold",
  "trigger_type": "sensor",
  "trigger_config": {
    "sensor_type": "temperature",
    "sensor_ids": ["sensor-001"]
  },
  "conditions": [
    {
      "type": "threshold",
      "parameter": "temperature",
      "operator": "greater_than",
      "value": 30
    }
  ],
  "actions": [
    {
      "type": "notification",
      "channels": ["sms", "email"],
      "recipients": ["facilities-team"]
    },
    {
      "type": "device_control",
      "device_id": "ac-unit-001",
      "action": "turn_on"
    }
  ],
  "enabled": true,
  "priority": "critical"
}
```

**Response:**
```json
{
  "id": "rule-002",
  "name": "Temperature Alert",
  "enabled": true,
  "created_at": "2024-12-29T17:15:00Z"
}
```

---

### Update Rule

Update an existing rule.

**Endpoint:** `PUT /rules/{rule_id}`

**Request:**
```json
{
  "enabled": false,
  "priority": "medium"
}
```

---

### Delete Rule

Delete an automation rule.

**Endpoint:** `DELETE /rules/{rule_id}`

**Response:**
```json
{
  "message": "Rule deleted successfully"
}
```

---

### Get Rule Execution History

Get history of rule executions.

**Endpoint:** `GET /rules/{rule_id}/history`

**Parameters:**
- `skip`, `limit` - Pagination
- `start_time`, `end_time` - Time range

**Response:**
```json
{
  "total": 45,
  "executions": [
    {
      "id": "exec-001",
      "rule_id": "rule-001",
      "triggered_at": "2024-12-29T02:30:00Z",
      "trigger_event": {
        "type": "person_detected",
        "event_id": "evt-12345"
      },
      "conditions_met": true,
      "actions_executed": [
        {
          "type": "notification",
          "status": "success",
          "details": "Sent to 3 recipients"
        },
        {
          "type": "recording",
          "status": "success",
          "details": "Started recording on 4 cameras"
        }
      ],
      "execution_time_ms": 245
    }
  ]
}
```

---

## Notifications

### Get Notifications

Get user notifications.

**Endpoint:** `GET /notifications`

**Parameters:**
- `skip`, `limit` - Pagination
- `status`: `all`, `unread`, `read`
- `type` - Filter by notification type

**Response:**
```json
{
  "total": 150,
  "unread_count": 12,
  "notifications": [
    {
      "id": "notif-001",
      "type": "person_detected",
      "title": "Person Detected - Main Entrance",
      "message": "Person detected at Main Entrance at 16:45",
      "event_id": "evt-12345",
      "camera_id": "cam-001",
      "thumbnail_url": "https://storage.example.com/thumbnails/evt-12345.jpg",
      "priority": "high",
      "is_read": false,
      "created_at": "2024-12-29T16:45:30Z"
    }
  ]
}
```

---

### Mark Notification as Read

Mark one or more notifications as read.

**Endpoint:** `PUT /notifications/{notification_id}/read`

Or mark all as read:

**Endpoint:** `PUT /notifications/read-all`

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

---

### Get Notification Preferences

Get user notification preferences.

**Endpoint:** `GET /notifications/preferences`

**Response:**
```json
{
  "user_id": "user-123",
  "channels": {
    "email": {
      "enabled": true,
      "address": "user@example.com"
    },
    "push": {
      "enabled": true
    },
    "sms": {
      "enabled": false,
      "phone_number": "+1234567890"
    }
  },
  "event_preferences": {
    "person_detected": {
      "channels": ["push", "email"],
      "min_confidence": 0.80
    },
    "vehicle_detected": {
      "channels": ["push"],
      "min_confidence": 0.75
    },
    "access_denied": {
      "channels": ["push", "email", "sms"],
      "min_confidence": 0.0
    }
  },
  "quiet_hours": {
    "enabled": true,
    "start_time": "23:00",
    "end_time": "07:00"
  }
}
```

---

### Update Notification Preferences

Update user notification preferences.

**Endpoint:** `PUT /notifications/preferences`

**Request:**
```json
{
  "channels": {
    "email": {
      "enabled": true
    },
    "push": {
      "enabled": true
    }
  },
  "quiet_hours": {
    "enabled": true,
    "start_time": "22:00",
    "end_time": "08:00"
  }
}
```

---

## Analytics

### Get Occupancy Data

Get occupancy statistics for a zone or site.

**Endpoint:** `GET /analytics/occupancy`

**Parameters:**
- `zone_id` or `site_id` - Location
- `start_time`, `end_time` - Time range
- `interval` - Data granularity: `minute`, `hour`, `day`

**Response:**
```json
{
  "zone_id": "zone-123",
  "zone_name": "Main Office Floor",
  "current_occupancy": 45,
  "max_capacity": 100,
  "time_range": {
    "start": "2024-12-29T00:00:00Z",
    "end": "2024-12-29T23:59:59Z"
  },
  "statistics": {
    "average": 38.5,
    "maximum": 67,
    "minimum": 5,
    "peak_time": "2024-12-29T14:30:00Z"
  },
  "data_points": [
    {
      "timestamp": "2024-12-29T09:00:00Z",
      "count": 12
    },
    {
      "timestamp": "2024-12-29T10:00:00Z",
      "count": 28
    }
  ]
}
```

---

### Get Traffic Analytics

Get traffic flow statistics.

**Endpoint:** `GET /analytics/traffic`

**Parameters:**
- `camera_id` - Specific camera
- `zone_id` - Specific zone
- `direction` - Filter by direction: `in`, `out`, `both`
- `start_time`, `end_time` - Time range

**Response:**
```json
{
  "camera_id": "cam-001",
  "direction": "both",
  "total_entries": 245,
  "total_exits": 238,
  "net_change": 7,
  "peak_hour": {
    "time": "2024-12-29T17:00:00Z",
    "entries": 45,
    "exits": 12
  },
  "hourly_data": [
    {
      "hour": "2024-12-29T09:00:00Z",
      "entries": 34,
      "exits": 5
    }
  ]
}
```

---

### Generate Report

Generate custom analytics report.

**Endpoint:** `POST /analytics/reports`

**Request:**
```json
{
  "report_type": "activity_summary",
  "parameters": {
    "site_id": "site-001",
    "start_date": "2024-12-01",
    "end_date": "2024-12-31",
    "include_charts": true,
    "include_details": true
  },
  "format": "pdf",
  "email_to": ["manager@example.com"]
}
```

**Response:**
```json
{
  "report_id": "report-001",
  "status": "generating",
  "estimated_completion": "2024-12-29T17:30:00Z"
}
```

Check status:

**Endpoint:** `GET /analytics/reports/{report_id}`

**Response:**
```json
{
  "report_id": "report-001",
  "status": "completed",
  "download_url": "https://storage.example.com/reports/report-001.pdf",
  "expires_at": "2024-12-30T17:30:00Z"
}
```

---

## System

### Health Check

Check system health.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "storage": "healthy",
    "mqtt": "healthy"
  },
  "timestamp": "2024-12-29T17:00:00Z"
}
```

---

### Get System Info

Get system information (Admin only).

**Endpoint:** `GET /system/info`

**Response:**
```json
{
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "active_cameras": 45,
  "active_users": 128,
  "total_events_today": 1250,
  "storage": {
    "total_gb": 5000,
    "used_gb": 3200,
    "available_gb": 1800,
    "usage_percent": 64
  },
  "performance": {
    "avg_response_time_ms": 145,
    "requests_per_second": 85
  }
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-12-29T17:00:00Z",
  "request_id": "req-12345"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `TOKEN_EXPIRED` | JWT token expired |
| `INVALID_TOKEN` | Malformed or invalid token |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `VALIDATION_ERROR` | Input validation failed |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVICE_UNAVAILABLE` | Service temporarily down |
| `CAMERA_OFFLINE` | Camera not accessible |
| `STORAGE_FULL` | Storage capacity reached |

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

**Default Limits:**
- **Authentication endpoints**: 10 requests/minute
- **General endpoints**: 100 requests/minute
- **Upload endpoints**: 20 requests/minute

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Rate Limit Exceeded Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

---

## Pagination

List endpoints support pagination:

**Request:**
```http
GET /api/cameras?skip=20&limit=10
```

**Response:**
```json
{
  "total": 150,
  "skip": 20,
  "limit": 10,
  "data": [...]
}
```

**Notes:**
- Default `limit`: 50
- Maximum `limit`: 100
- Use `skip` for offset-based pagination

---

## Filtering & Sorting

**Filtering:**
```http
GET /api/events?event_type=person&min_confidence=0.85
```

**Sorting:**
```http
GET /api/cameras?sort_by=name&order=asc
```

**Multiple Filters:**
```http
GET /api/events?camera_id=cam-001&start_time=2024-12-29T00:00:00Z&end_time=2024-12-29T23:59:59Z
```

---

## Webhooks

Register webhooks to receive real-time event notifications.

**Register Webhook:**
```http
POST /api/webhooks
```

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["person_detected", "vehicle_detected", "access_denied"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload:**
```json
{
  "event_type": "person_detected",
  "timestamp": "2024-12-29T17:00:00Z",
  "data": {
    "event_id": "evt-12345",
    "camera_id": "cam-001",
    "confidence": 0.95
  },
  "signature": "sha256=..."
}
```

---

## SDK Examples

### Python

```python
import requests

# Authentication
response = requests.post(
    "https://your-domain.com/api/auth/login",
    data={
        "username": "user@example.com",
        "password": "password"
    }
)
token = response.json()["access_token"]

# Get cameras
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://your-domain.com/api/cameras",
    headers=headers
)
cameras = response.json()["cameras"]
```

### JavaScript

```javascript
// Authentication
const response = await fetch('https://your-domain.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user@example.com&password=password'
});
const { access_token } = await response.json();

// Get events
const events = await fetch('https://your-domain.com/api/events', {
  headers: { 'Authorization': `Bearer ${access_token}` }
}).then(r => r.json());
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST https://your-domain.com/api/auth/login \
  -d "username=user@example.com&password=password" \
  | jq -r '.access_token')

# Get cameras
curl https://your-domain.com/api/cameras \
  -H "Authorization: Bearer $TOKEN"
```

---

## API Changelog

### Version 1.0.0 (Current)
- Initial API release
- Full CRUD operations for all resources
- Webhook support
- Rate limiting

### Upcoming (1.1.0)
- GraphQL endpoint
- Batch operations
- Advanced filtering
- WebSocket support for real-time events

---

**For additional support or API questions, contact: api-support@example.com**
