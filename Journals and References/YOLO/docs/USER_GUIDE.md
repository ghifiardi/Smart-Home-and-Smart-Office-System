# User Guide

**Smart Office/Home Surveillance System**

Complete guide for end users and administrators to use the surveillance system.

Version: 1.0.0
Last Updated: December 29, 2024

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Cameras](#managing-cameras)
4. [Viewing Live Feeds](#viewing-live-feeds)
5. [Reviewing Recordings](#reviewing-recordings)
6. [Detection Events](#detection-events)
7. [Access Control](#access-control)
8. [Automation Rules](#automation-rules)
9. [Notifications](#notifications)
10. [Reports & Analytics](#reports--analytics)
11. [User Management](#user-management)
12. [Mobile App](#mobile-app)

---

## Getting Started

### First Time Login

1. **Access the Dashboard**
   - Open your web browser
   - Navigate to: `https://your-domain.com`
   - You'll see the login screen

2. **Login Credentials**
   - Enter your email address
   - Enter your password
   - Click "Sign In"

   **Default Admin Credentials** (change immediately after first login):
   ```
   Email: admin@smartoffice.com
   Password: password123
   ```

3. **Change Your Password**
   - Click on your profile icon (top right)
   - Select "Settings"
   - Go to "Security" tab
   - Enter current password
   - Enter new password (minimum 8 characters)
   - Click "Update Password"

### User Roles

The system supports different user roles with varying permissions:

| Role | Permissions |
|------|-------------|
| **Super Admin** | Full system access, user management, all configurations |
| **Admin** | Site management, camera setup, view all feeds |
| **Security** | View live feeds, review events, create reports |
| **Manager** | View analytics, review reports, limited camera access |
| **User** | View assigned cameras only, receive notifications |
| **Viewer** | Read-only access to live feeds and recordings |

---

## Dashboard Overview

The dashboard is your central hub for monitoring and managing the surveillance system.

### Main Dashboard Components

#### 1. **Status Overview**
Located at the top of the dashboard:
- **Active Cameras**: Shows number of cameras currently online
- **Recent Events**: Count of detection events in last 24 hours
- **System Health**: Overall system status indicator
- **Storage Usage**: Available storage space

#### 2. **Live Camera Grid**
Central section showing:
- Live video feeds from selected cameras
- Camera name and location
- Recording status indicator
- Click any camera to view full screen

#### 3. **Recent Events Panel**
Right sidebar showing:
- Latest detection events
- Event type (person, vehicle, motion)
- Timestamp
- Camera location
- Thumbnail image
- Click event for details

#### 4. **Quick Actions**
Left sidebar with shortcuts:
- Add Camera
- View All Events
- Create Report
- Manage Rules
- Settings

### Navigation Menu

Located on the left side:

```
📊 Dashboard          - Main overview
📹 Cameras            - Camera management
🎬 Live View         - Live camera feeds
📼 Recordings        - Recorded videos
🔔 Events            - Detection events
🚪 Access Control    - Door/gate management
⚙️  Rules            - Automation rules
📊 Analytics         - Reports and insights
👥 Users             - User management (Admin only)
⚙️  Settings         - System settings
```

---

## Managing Cameras

### Adding a New Camera

1. **Navigate to Cameras**
   - Click "Cameras" in the left menu
   - Click "+ Add Camera" button

2. **Enter Camera Details**
   ```
   Camera Name:        Main Entrance
   Location:           Building A - Floor 1
   Zone:              Entrance
   Camera Type:        IP Camera
   ```

3. **Configure Connection**
   ```
   Connection Type:    RTSP
   Stream URL:        rtsp://192.168.1.100:554/stream1
   Username:          admin
   Password:          ********
   ```

4. **Test Connection**
   - Click "Test Connection"
   - Wait for live preview to appear
   - If successful, you'll see the camera feed

5. **Configure Settings**
   ```
   Resolution:         1920x1080 (Full HD)
   Frame Rate:         15 FPS
   Recording Mode:     Continuous
   Motion Detection:   Enabled
   ```

6. **Save Camera**
   - Click "Save Camera"
   - Camera will appear in your camera list

### Editing Camera Settings

1. Go to "Cameras" page
2. Find the camera you want to edit
3. Click the "Edit" icon (pencil)
4. Modify settings as needed
5. Click "Save Changes"

### Common Camera Settings

#### **Video Settings**
- **Resolution**: Higher resolution = better quality but more storage
  - 4K (3840x2160) - Best quality
  - Full HD (1920x1080) - Recommended
  - HD (1280x720) - Good for most cases
  - SD (640x480) - Minimal storage

- **Frame Rate**: Frames per second
  - 30 FPS - Smooth video (high bandwidth)
  - 15 FPS - Recommended (balanced)
  - 10 FPS - Low bandwidth
  - 5 FPS - Motion detection only

#### **Recording Settings**
- **Continuous**: Record 24/7
- **Motion Detection**: Record only when motion detected
- **Scheduled**: Record during specific hours
- **Event-Based**: Record when specific events occur

#### **Detection Settings**
- **Person Detection**: AI-powered person detection
- **Vehicle Detection**: Detect cars, trucks, motorcycles
- **Face Recognition**: Identify registered persons
- **Motion Detection**: Basic motion-based detection

### Camera Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Green dot | Camera online and recording |
| 🟡 Yellow dot | Camera online but not recording |
| 🔴 Red dot | Camera offline or error |
| ⚫ Gray dot | Camera disabled |

---

## Viewing Live Feeds

### Live View Page

1. **Access Live View**
   - Click "Live View" in the left menu
   - Select camera layout (1x1, 2x2, 3x3, 4x4)

2. **Camera Controls**
   Each camera tile has controls:
   - **🔊 Audio**: Toggle audio on/off
   - **📷 Snapshot**: Take a screenshot
   - **📹 Record**: Start manual recording
   - **🔍 Zoom**: Digital zoom (pinch or scroll)
   - **⚙️ Settings**: Quick camera settings
   - **⛶ Full Screen**: Expand to full screen

3. **Camera Groups**
   - Create groups for quick viewing
   - Example: "All Entrances", "Parking Lot", "Office Floors"
   - Switch between groups using dropdown

### PTZ Camera Control

For Pan-Tilt-Zoom cameras:

1. **Click on camera** to select it
2. **Use PTZ Controls**:
   - Arrow buttons to pan/tilt
   - +/- buttons to zoom
   - "Home" button to return to preset position
3. **Save Presets**:
   - Move camera to desired position
   - Click "Save Preset"
   - Name the preset (e.g., "Entrance", "Parking")
4. **Recall Presets**:
   - Click preset name to move camera

### Multi-Camera View

**Layout Options:**
- **1x1**: Single camera (full screen)
- **2x2**: Four cameras
- **3x3**: Nine cameras
- **4x4**: Sixteen cameras
- **Custom**: Drag and resize camera windows

**Tips for Multi-Camera Viewing:**
- Click any camera to maximize
- Right-click for camera menu
- Drag cameras to rearrange
- Double-click for full screen

---

## Reviewing Recordings

### Search for Recordings

1. **Go to Recordings Page**
   - Click "Recordings" in menu

2. **Filter Recordings**
   ```
   Camera:           Select camera or "All Cameras"
   Date Range:       Select start and end date
   Time Range:       Select specific hours
   Event Type:       All, Person, Vehicle, Motion
   ```

3. **Search**
   - Click "Search"
   - Results appear as timeline

### Playback Controls

**Timeline View:**
- Blue bars indicate recorded footage
- Red marks indicate events (person/vehicle detected)
- Click anywhere on timeline to jump to that time

**Playback Buttons:**
- ⏮️ Previous event
- ⏯️ Play/Pause
- ⏭️ Next event
- 🔁 Loop
- ⏩ Speed (0.5x, 1x, 2x, 4x, 8x)
- 🔊 Volume

### Exporting Videos

1. **Select Time Range**
   - Click "Export" button
   - Choose start time
   - Choose end time

2. **Export Options**
   ```
   Format:           MP4 (recommended), AVI, MOV
   Resolution:       Original, 1080p, 720p, 480p
   Include Audio:    Yes/No
   Watermark:        Add timestamp and camera name
   ```

3. **Export**
   - Click "Export Video"
   - Wait for processing (may take a few minutes)
   - Download link will appear when ready
   - Video saved to Downloads folder

### Creating Video Clips

For sharing specific incidents:

1. In playback mode, find the incident
2. Click "Create Clip"
3. Adjust start/end markers
4. Add description
5. Click "Save Clip"
6. Clip available in "My Clips"

---

## Detection Events

### Viewing Events

1. **Events Dashboard**
   - Click "Events" in menu
   - See all recent detection events

2. **Event Information**
   Each event shows:
   - Thumbnail image
   - Event type (Person, Vehicle, Motion)
   - Confidence score (% accuracy)
   - Camera name and location
   - Date and time
   - Duration

3. **Event Actions**
   - 👁️ View: See full event details
   - 📹 Play: Watch video clip
   - 📥 Download: Download clip
   - 🗑️ Delete: Remove event
   - ⚠️ Report: Flag as important

### Event Details

Click any event to see:

**Event Information:**
- Full-size snapshot
- Video playback
- Detection bounding boxes
- Confidence scores

**Person Detection Details:**
- Number of persons
- Position in frame
- Face recognition results (if enabled)
- Time in frame

**Vehicle Detection Details:**
- Vehicle type (car, truck, motorcycle)
- License plate (if visible)
- Direction of travel
- Speed (if configured)

### Searching Events

**Quick Filters:**
- Today
- Last 7 Days
- Last 30 Days
- Custom Range

**Advanced Search:**
```
Camera:          Select specific camera(s)
Event Type:      Person, Vehicle, Motion, Face
Date Range:      Start and end date
Time Range:      Specific hours
Confidence:      Minimum detection confidence (%)
Zone:            Specific zones only
```

### Event Notifications

**Configure Notifications:**
1. Go to Settings → Notifications
2. Choose notification channels:
   - 📧 Email
   - 📱 Push Notification
   - 💬 SMS
   - 🔔 In-App
3. Set notification rules:
   - Which events trigger notifications
   - Quiet hours (don't notify during sleep)
   - Notification frequency (immediate, summary)

**Example Rules:**
```
Rule: Person in restricted area
  When: Person detected
  Where: Restricted zones
  Time: After business hours (6 PM - 6 AM)
  Action: Send immediate push notification + email
```

---

## Access Control

### Managing Access Points

Access points include doors, gates, turnstiles, and barriers.

#### Add Access Point

1. **Navigate to Access Control**
   - Click "Access Control" in menu
   - Click "+ Add Device"

2. **Device Configuration**
   ```
   Device Name:       Main Entrance Door
   Device Type:       Door Lock
   Location:          Building A - Main Entrance
   Connection:        MQTT
   Device ID:         door-001
   ```

3. **Access Settings**
   ```
   Access Mode:       Card + PIN
   Valid Cards:       Employee badges
   Unlock Duration:   5 seconds
   Auto-Lock:         Enabled
   ```

### Access Events

**View Access Log:**
- See all door access attempts
- Filter by person, door, time
- Export access reports

**Event Types:**
- ✅ Access Granted
- ❌ Access Denied
- ⚠️ Forced Entry
- 🔓 Manual Unlock
- 🔒 Manual Lock

### Managing Access Cards

#### Register New Card

1. Go to Access Control → Cards
2. Click "+ Add Card"
3. **Scan Card** or enter card number
4. **Assign to User**:
   ```
   Card Number:      12345678
   Card Holder:      John Doe
   Valid From:       2024-01-01
   Valid Until:      2024-12-31
   Access Level:     Standard Employee
   ```
5. Click "Save Card"

#### Access Levels

Create access levels to group permissions:

**Example Access Levels:**

| Level | Description | Access |
|-------|-------------|--------|
| **Admin** | Full building access | All doors, 24/7 |
| **Employee** | Standard office access | Office areas, 6 AM - 10 PM |
| **Visitor** | Limited access | Lobby and meeting rooms only |
| **Contractor** | Temporary access | Specific areas, time-limited |

### Remote Door Control

**Unlock Door Remotely:**
1. Go to Live View or Access Control
2. Find the door you want to control
3. Click "Unlock" button
4. Door unlocks for configured duration (default: 5 seconds)

**Grant Temporary Access:**
1. Go to Access Control
2. Select the door
3. Click "Grant Temporary Access"
4. Choose duration (15 min, 1 hour, 4 hours, 8 hours)
5. Door remains unlocked for selected time

---

## Automation Rules

Create intelligent automation rules to respond to events automatically.

### Creating a Rule

1. **Navigate to Rules**
   - Click "Rules" in menu
   - Click "+ Create Rule"

2. **Rule Configuration**

**Step 1: Name and Description**
```
Rule Name:         After Hours Intrusion Alert
Description:       Alert security when person detected after hours
```

**Step 2: Choose Trigger**
```
Trigger Type:      Event Detection
Event:             Person Detected
```

**Step 3: Set Conditions**
```
Conditions:
  ✓ Time is between 6:00 PM and 6:00 AM
  ✓ Zone is "Restricted Area"
  ✓ Confidence > 80%
```

**Step 4: Define Actions**
```
Actions:
  ✓ Send push notification to security team
  ✓ Send email to admin@company.com
  ✓ Start recording on all nearby cameras
  ✓ Lock all doors in the building
  ✓ Sound alarm
```

**Step 5: Review and Save**
- Review all settings
- Click "Save Rule"
- Toggle "Enabled" to activate

### Example Automation Rules

#### 1. Visitor Management
```yaml
Name: Visitor Arrival Notification
Trigger: Person detected at main entrance
Conditions:
  - Time: During business hours
  - Face: Unknown person
Actions:
  - Notify reception desk
  - Capture and save image
  - Display on reception monitor
```

#### 2. Parking Lot Security
```yaml
Name: After Hours Parking Alert
Trigger: Vehicle detected in parking lot
Conditions:
  - Time: 10:00 PM - 6:00 AM
  - Location: Employee parking lot
Actions:
  - Alert security
  - Record vehicle for 5 minutes
  - Turn on parking lot lights
```

#### 3. Temperature Alert
```yaml
Name: Server Room Temperature Alert
Trigger: Temperature reading
Conditions:
  - Temperature > 30°C
  - Location: Server room
Actions:
  - Send critical alert to IT team
  - Send SMS to facilities manager
  - Turn on additional AC units
  - Create incident report
```

#### 4. Access Denial Response
```yaml
Name: Multiple Failed Access Attempts
Trigger: Access denied
Conditions:
  - Failed attempts > 3 in 5 minutes
  - Same card or location
Actions:
  - Alert security immediately
  - Disable card temporarily
  - Record camera footage
  - Log security incident
```

### Rule Management

**Enable/Disable Rules:**
- Toggle switch next to rule name
- Disabled rules don't trigger

**Edit Rules:**
- Click rule name
- Modify any settings
- Save changes

**Rule History:**
- View when rule was triggered
- See action results
- Review effectiveness

**Rule Templates:**
The system includes pre-built templates:
- Intrusion Detection
- After Hours Activity
- Visitor Management
- Temperature Alerts
- Occupancy Limits
- Emergency Response

---

## Notifications

### Notification Channels

#### Email Notifications
- Detailed event information
- Includes snapshot images
- Good for non-urgent alerts
- Can include video clips

#### Push Notifications
- Instant mobile alerts
- Tap to view event
- Good for urgent alerts
- Includes thumbnail

#### SMS Notifications
- Critical alerts only
- Short message with link
- Useful when no internet
- Carrier charges may apply

#### In-App Notifications
- Real-time alerts in dashboard
- Click to view details
- Notification history
- Badge counter

### Managing Notification Preferences

1. **Go to Settings → Notifications**

2. **General Settings**
   ```
   Enable Notifications:        ✓ Yes
   Quiet Hours:                 11:00 PM - 7:00 AM
   Summary Mode:                Send daily summary at 8:00 AM
   ```

3. **Event Preferences**
   ```
   Person Detection:
     - Email:                   ✓ Enabled
     - Push:                    ✓ Enabled
     - SMS:                     ⬜ Disabled
     - Minimum Confidence:      80%

   Vehicle Detection:
     - Email:                   ✓ Enabled
     - Push:                    ⬜ Disabled
     - SMS:                     ⬜ Disabled

   Access Denied:
     - Email:                   ✓ Enabled
     - Push:                    ✓ Enabled
     - SMS:                     ✓ Enabled (critical)
   ```

4. **Camera-Specific Settings**
   - Choose cameras to monitor
   - Some cameras send more alerts
   - Others may be monitoring only

### Notification Examples

**Email Notification:**
```
Subject: [ALERT] Person Detected - Main Entrance

Event Details:
- Type: Person Detection
- Camera: Main Entrance Camera
- Location: Building A - Floor 1
- Time: 2024-12-29 02:35:14 AM
- Confidence: 95%

[Snapshot Image]

View full event: https://your-domain.com/events/123

---
Smart Office Surveillance System
```

**Push Notification:**
```
🔴 Person Detected
Main Entrance - 2:35 AM
Tap to view
```

**SMS:**
```
ALERT: Person detected at Main Entrance at 2:35 AM.
View: https://your-domain.com/e/123
```

---

## Reports & Analytics

### Pre-built Reports

#### 1. **Activity Summary**
Daily/weekly/monthly summary of:
- Total events detected
- Events by type
- Peak activity hours
- Busiest cameras

#### 2. **Occupancy Report**
Track people count over time:
- Current occupancy
- Max occupancy
- Average occupancy
- Occupancy heatmap

#### 3. **Access Report**
Access control statistics:
- Total access events
- Access granted vs denied
- Most accessed doors
- Access by person

#### 4. **Incident Report**
Security incidents:
- Intrusion attempts
- After-hours activity
- Access violations
- System alerts

### Generating Reports

1. **Go to Analytics → Reports**

2. **Choose Report Type**
   - Select from report templates

3. **Set Parameters**
   ```
   Report Period:     Last 30 days
   Cameras:           All or specific cameras
   Include:
     ✓ Charts and graphs
     ✓ Detailed tables
     ✓ Event snapshots
     ⬜ Video clips (large file size)
   ```

4. **Generate Report**
   - Click "Generate Report"
   - Processing may take a few minutes
   - Receive notification when ready

5. **View and Export**
   - View in browser
   - Export as PDF
   - Export as Excel
   - Email to recipients

### Analytics Dashboard

**Traffic Analytics:**
- People counting
- Entry/exit tracking
- Dwell time analysis
- Zone heatmaps

**Trend Analysis:**
- Activity patterns over time
- Peak hours identification
- Day-of-week patterns
- Seasonal trends

**Performance Metrics:**
- Camera uptime
- Detection accuracy
- System health
- Storage usage

### Custom Dashboards

Create personalized dashboards:

1. Go to Analytics → Custom Dashboard
2. Click "+ Add Widget"
3. Choose widget type:
   - Live camera feed
   - Event counter
   - Chart/graph
   - Status indicator
   - Recent events list
4. Configure widget
5. Arrange layout
6. Save dashboard

---

## User Management

*For Admin users only*

### Adding New Users

1. **Go to Users → Add User**

2. **User Information**
   ```
   Full Name:         Jane Smith
   Email:            jane.smith@company.com
   Username:         jsmith
   Role:             Security
   ```

3. **Permissions**
   ```
   Camera Access:     Select specific cameras or "All"
   Features:
     ✓ View live feeds
     ✓ View recordings
     ✓ Export videos
     ⬜ Manage cameras (admin only)
     ⬜ Manage users (admin only)
   ```

4. **Notification Settings**
   - Configure default notifications
   - User can modify later

5. **Create User**
   - Click "Create User"
   - User receives welcome email with temporary password
   - User must change password on first login

### Managing Existing Users

**Edit User:**
- Change permissions
- Update camera access
- Modify role

**Disable User:**
- Temporarily disable access
- User can't login but data preserved

**Delete User:**
- Permanently remove user
- All user data deleted

### User Activity Log

View what users are doing:
- Login/logout events
- Cameras viewed
- Videos exported
- Settings changed
- Reports generated

---

## Mobile App

### Installing the App

**iOS:**
1. Open App Store
2. Search "Smart Office Surveillance"
3. Tap "Get" to install

**Android:**
1. Open Google Play Store
2. Search "Smart Office Surveillance"
3. Tap "Install"

### Mobile App Features

#### Live View
- View camera feeds on mobile
- Supports multiple camera layouts
- Pinch to zoom
- Rotate for landscape mode

#### Events
- Receive push notifications
- View event history
- Watch event clips
- Share events

#### Quick Actions
- Unlock doors remotely
- Trigger manual recording
- Take snapshots
- Enable/disable rules

#### Offline Mode
- View cached recordings
- See recent events
- Access saved clips

### Mobile App Settings

```
Settings → Mobile App:
  ✓ Enable push notifications
  ✓ Use cellular data for live view
  ✓ Download events on WiFi only
  ✓ Auto-play event videos
  Video Quality: Auto (adjusts to connection)
  Cache Size: 1 GB
```

---

## Frequently Asked Questions

### General

**Q: How long are recordings kept?**
A: Default is 30 days. Contact your administrator to change retention period.

**Q: Can I access the system from outside the office?**
A: Yes, with proper authentication. Use your same login credentials.

**Q: What happens if internet connection is lost?**
A: Cameras continue recording locally. You can access recordings once connection restored.

### Camera Issues

**Q: Camera shows "Offline" status**
A: Check if camera has power and network connection. Contact support if issue persists.

**Q: Live feed is laggy or choppy**
A: Reduce video quality in camera settings or check network bandwidth.

**Q: Can I add my own cameras?**
A: Yes, if you have admin permissions. Most IP cameras with RTSP support work.

### Events & Notifications

**Q: Too many false motion detections**
A: Adjust sensitivity settings or use AI-powered person/vehicle detection instead.

**Q: Not receiving notifications**
A: Check notification settings and ensure app has notification permissions.

**Q: Can I customize what triggers notifications?**
A: Yes, go to Settings → Notifications and configure per event type.

### Access Control

**Q: My card doesn't work**
A: Contact administrator to verify card is registered and active.

**Q: Can I unlock door from my phone?**
A: Yes, if you have appropriate permissions in the mobile app.

**Q: How do I grant temporary access to a visitor?**
A: Use the Access Control page to create temporary access or visitor pass.

---

## Getting Help

### Support Resources

- **Help Center**: https://support.example.com
- **Email Support**: support@example.com
- **Phone**: 1-800-XXX-XXXX
- **Live Chat**: Available in-app (bottom right corner)

### Training Videos

Access video tutorials:
1. Click Help (?) icon in top right
2. Select "Video Tutorials"
3. Choose topic

Topics include:
- Getting Started
- Adding Cameras
- Creating Rules
- Generating Reports
- Mobile App Guide

---

**Welcome to Smart Office/Home Surveillance System! 🏢🏠**

For technical support or feature requests, please contact your system administrator.
