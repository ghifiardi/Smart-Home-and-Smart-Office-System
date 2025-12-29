# Smart Office/Home Surveillance System 🏢🏠

**AI-Powered Video Surveillance with Intelligent Detection and Automation**

A comprehensive, microservices-based surveillance system designed for smart offices and homes, featuring real-time video processing, AI-powered object detection, facial recognition, access control, and intelligent automation.

[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Documentation](https://img.shields.io/badge/docs-complete-success.svg)](docs/README.md)

---

## 🌟 Key Features

### 🎥 Video Surveillance
- **Multi-Camera Support** - Manage unlimited IP cameras
- **Live Streaming** - Real-time RTSP video feeds
- **Recording** - Continuous, motion-based, or scheduled recording
- **Multi-View** - View 1-16 cameras simultaneously
- **PTZ Control** - Pan-Tilt-Zoom camera support

### 🤖 AI-Powered Detection
- **Person Detection** - YOLOv8-based person detection
- **Vehicle Detection** - Detect cars, trucks, motorcycles
- **Face Recognition** - DeepFace-powered facial recognition
- **Motion Detection** - Advanced motion-based alerts
- **Anomaly Detection** - Identify unusual patterns

### 🚪 Access Control
- **Smart Locks** - Remote door/gate control
- **Card Management** - RFID/NFC badge system
- **Access Levels** - Role-based access permissions
- **Access Logs** - Complete audit trail
- **Visitor Management** - Temporary access codes

### ⚙️ Intelligent Automation
- **Rule Engine** - Create custom automation rules
- **Event Triggers** - Respond to detections automatically
- **Scheduled Actions** - Time-based automation
- **Multi-Action** - Execute multiple actions per rule
- **Condition Logic** - Complex conditional rules

### 📊 Analytics & Reporting
- **Occupancy Tracking** - Real-time people counting
- **Traffic Analysis** - Entry/exit statistics
- **Heatmaps** - Activity visualization
- **Custom Reports** - Detailed analytics reports
- **Trend Analysis** - Historical pattern analysis

### 🔔 Notifications
- **Multi-Channel** - Email, SMS, push notifications
- **Real-Time Alerts** - Instant event notifications
- **Custom Rules** - Configurable notification rules
- **Quiet Hours** - Schedule notification preferences
- **Priority Levels** - Critical, high, medium, low alerts

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop 24.0+
- Docker Compose 2.20+
- Python 3.11+
- 8GB+ RAM
- 20GB+ disk space

### Installation (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/ghifiardi/Smart-Home-and-Smart-Office-System.git
cd Smart-Home-and-Smart-Office-System

# 2. Start infrastructure services
cd surveillance-system
docker-compose up -d postgres redis minio emqx

# 3. Load sample data
cd ..
./scripts/load_seed_data.sh

# 4. Start application services
cd surveillance-system
docker-compose up -d

# 5. Access dashboard
open http://localhost:8001
```

**Default Credentials:**
- Email: `admin@smartoffice.com`
- Password: `password123`

**Full Setup Guide:** [Quick Start Guide](QUICK_START_GUIDE.md)

---

## 📚 Documentation

### For End Users
- **[User Guide](docs/USER_GUIDE.md)** - Complete guide for daily use
- **[Quick Start](QUICK_START_GUIDE.md)** - Get started in 10 minutes
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solve common issues

### For Developers
- **[Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)** - System design
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development setup
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

### For Operations
- **[Operations Guide](docs/OPERATIONS_GUIDE.md)** - Deployment & maintenance
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - System diagnostics

**Complete Documentation:** [docs/README.md](docs/README.md)

---

## 🏗 Architecture

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
    ┌────▼────┐  ┌──────────┐  ┌──────────┐  ┌─▼──────────┐
    │  Auth   │  │   Data   │  │Detection │  │  Device    │
    │ Service │  │ Service  │  │ Service  │  │ Controller │
    └────┬────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘
         │            │             │              │
    ┌────▼────┐  ┌───▼────┐   ┌────▼─────┐   ┌────▼────┐
    │  Rule   │  │Notif.  │   │Analytics │   │  MQTT   │
    │ Engine  │  │Service │   │ Service  │   │  Broker │
    └────┬────┘  └────────┘   └──────────┘   └─────────┘
         │
    ┌────▼────────────────────────────────────────────────┐
    │  Infrastructure (PostgreSQL, Redis, MinIO, EMQX)   │
    └─────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL + TimescaleDB
- Redis
- MinIO (S3-compatible storage)
- EMQX (MQTT broker)

**AI/ML:**
- YOLOv8 (Object detection)
- DeepFace (Face recognition)
- PyTorch
- OpenCV

**Frontend:**
- React (Dashboard)
- WebSocket (Real-time updates)
- Material-UI

**DevOps:**
- Docker & Docker Compose
- Kubernetes (production)
- Prometheus & Grafana (monitoring)

---

## 💻 System Requirements

### Minimum (1-5 cameras)
- CPU: 4 cores
- RAM: 8 GB
- Storage: 500 GB
- Network: 100 Mbps

### Recommended (5-20 cameras)
- CPU: 8 cores
- RAM: 16 GB
- Storage: 2 TB
- Network: 1 Gbps
- GPU: NVIDIA GPU with 4GB VRAM

### Enterprise (20+ cameras)
- CPU: 16+ cores
- RAM: 32+ GB
- Storage: 5+ TB (SSD)
- Network: 10 Gbps
- GPU: NVIDIA GPU with 8GB+ VRAM

---

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -r scripts/tests/requirements.txt

# Run integration tests
./scripts/run_auth_tests.sh all

# Run security tests
./scripts/run_auth_tests.sh security

# Run service health checks
./scripts/test_services.sh
```

**Test Coverage:**
- 30+ Integration tests
- 15+ Security tests
- Service health checks
- API endpoint tests

**Testing Documentation:** [scripts/tests/README.md](scripts/tests/README.md)

---

## 📱 Mobile Apps

### iOS
- Download from App Store
- Supports iOS 14+
- Live view, notifications, remote control

### Android
- Download from Google Play
- Supports Android 8+
- Full feature parity with iOS

---

## 🔐 Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Password encryption (bcrypt)

### Data Security
- TLS/SSL encryption in transit
- Data encryption at rest
- Secure credential storage
- API rate limiting

### Compliance
- GDPR compliance features
- Audit logging
- Data retention policies
- Privacy controls

**Security Details:** [Technical Architecture - Security](docs/TECHNICAL_ARCHITECTURE.md#security-architecture)

---

## 🌍 Deployment Options

### Docker Compose (Small Scale)
```bash
docker-compose up -d
```

### Kubernetes (Medium-Large Scale)
```bash
kubectl apply -f deployment/kubernetes/
```

### Cloud Platforms
- AWS (ECS, EKS)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)

**Deployment Guide:** [Operations Guide - Deployment](docs/OPERATIONS_GUIDE.md#deployment)

---

## 📊 Sample Data

The system includes comprehensive sample data:

- **7 Users** - Various roles (admin, security, user)
- **4 Sites** - Jakarta, Surabaya, Bandung, Tangerang
- **10 Cameras** - Different locations and types
- **4 Access Devices** - Doors and gates
- **5 Sensors** - Temperature, humidity, air quality
- **7 Registered Persons** - For face recognition
- **5 Automation Rules** - Pre-configured examples

**Load Sample Data:**
```bash
./scripts/load_seed_data.sh
```

**Seed Data Guide:** [scripts/SEED_DATA_README.md](scripts/SEED_DATA_README.md)

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Contributing Guidelines:** [Developer Guide - Contributing](docs/DEVELOPER_GUIDE.md#contributing)

---

## 📝 License

This project is proprietary software. See [LICENSE](LICENSE) for details.

**License Tiers:**
- Free Trial: 30 days, up to 4 cameras
- Standard: Up to 16 cameras
- Professional: Up to 64 cameras
- Enterprise: Unlimited cameras

---

## 🆘 Support

### Documentation
- 📖 [User Guide](docs/USER_GUIDE.md)
- 💻 [Developer Guide](docs/DEVELOPER_GUIDE.md)
- 🛠 [Troubleshooting](docs/TROUBLESHOOTING.md)

### Community & Support
- 💬 **Community Forum**: https://community.example.com
- 📧 **Email**: support@example.com
- 📞 **Phone**: 1-800-XXX-XXXX
- 🎫 **Support Portal**: https://support.example.com

### Training
- 🎥 Video Tutorials (in-app)
- 📚 Online Courses
- 👥 Monthly Webinars
- 🏢 On-site Training (Enterprise)

---

## 🗺 Roadmap

### Version 1.1.0 (Q1 2025)
- [ ] License plate recognition
- [ ] Thermal camera support
- [ ] Advanced analytics
- [ ] Improved mobile app

### Version 1.2.0 (Q2 2025)
- [ ] Multi-site management
- [ ] Cloud recording backup
- [ ] API webhooks
- [ ] Custom integrations

### Version 2.0.0 (Q3 2025)
- [ ] Edge computing support
- [ ] 5G camera support
- [ ] Advanced AI models
- [ ] Blockchain audit trail

---

## 📸 Screenshots

### Dashboard
![Dashboard Overview](assets/dashboard.png)

### Live View
![Multi-Camera View](assets/live-view.png)

### Detection Events
![Detection Events](assets/events.png)

### Analytics
![Analytics Dashboard](assets/analytics.png)

---

## 🙏 Acknowledgments

This system uses the following open-source projects:

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **Redis** - Caching
- **YOLOv8** - Object detection
- **DeepFace** - Face recognition
- **Docker** - Containerization

See [THIRD_PARTY_LICENSES](THIRD_PARTY_LICENSES.md) for complete list.

---

## 📞 Contact

**Developer:** Raditio Ghifari
**Email:** raditio.ghifiardi@gmail.com
**GitHub:** [@ghifiardi](https://github.com/ghifiardi)

**Company Website:** https://www.example.com
**Sales:** sales@example.com
**Support:** support@example.com

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=ghifiardi/Smart-Home-and-Smart-Office-System&type=Date)](https://star-history.com/#ghifiardi/Smart-Home-and-Smart-Office-System&Date)

---

**Built with ❤️ using Claude Code**

*Last Updated: December 29, 2024*
