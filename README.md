# PulseGuard Real-Time Uptime Monitoring System

PulseGuard is a lightweight real-time uptime monitoring system developed using **Flask, Docker, and SQLite**. It is designed to monitor websites, IP devices, and TCP services while providing live status tracking, response time monitoring, uptime statistics, history logs, and Telegram alert integration.

The main goal of this project is to understand how real-world monitoring systems work behind the scenes and to gain hands-on experience with backend development, Docker containerization, scheduling systems, APIs, and real-time monitoring concepts.

---

## Features

- Real-time monitoring dashboard
- HTTP / HTTPS monitoring
- Ping / ICMP monitoring
- TCP port monitoring
- Uptime percentage tracking
- Response time monitoring
- Monitoring history logs
- Live dashboard updates
- Telegram alert notifications
- Dockerized deployment
- Login authentication system
- Lightweight SQLite database
- Search and filtering support
- Incident status display
- Response history visualization

---

## Technologies Used

### Backend

- Python
- Flask
- APScheduler

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Database

- SQLite

### DevOps & Tools

- Docker
- Docker Compose
- Git
- GitHub
- Ngrok

### Notification Service

- Telegram Bot API

---

## Project Architecture

```text
User Browser
     |
     v
Frontend Dashboard
HTML / CSS / JavaScript
     |
     v
Flask Backend API
     |
     v
Monitoring Engine
APScheduler
     |
     v
SQLite Database
     |
     v
Telegram Alert System
```

---

## Monitoring Types

PulseGuard supports three types of monitoring: **HTTP / HTTPS Monitoring**, **Ping / ICMP Monitoring**, and **TCP Port Monitoring**.

---

### 1. HTTP / HTTPS Monitoring

HTTP monitoring checks whether a website, web application, or API endpoint is accessible using HTTP or HTTPS requests.

#### Example

```text
https://google.com
```

#### Use Cases

- Website uptime monitoring
- Web application availability checks
- API endpoint monitoring
- Public service health checks

---

### 2. Ping / ICMP Monitoring

Ping monitoring uses ICMP requests to check whether a device or server is reachable over the network.

#### Example

```text
192.168.1.1
```

#### Use Cases

- Router availability monitoring
- Server reachability checks
- Local network device monitoring
- Infrastructure health checks

---

### 3. TCP Port Monitoring

TCP monitoring checks whether a specific service port is open and accepting connections.

#### Example

```text
192.168.1.10:22
```

#### Use Cases

- SSH service monitoring
- Redis port monitoring
- Database port monitoring
- Web server port checks
- Custom service availability checks

---

## How PulseGuard Works

1. The user logs in to the PulseGuard dashboard.
2. The user adds a new monitor from the dashboard.
3. Monitor details are stored in the SQLite database.
4. APScheduler runs monitoring checks automatically at fixed intervals.
5. Flask backend performs HTTP, Ping, or TCP checks based on the monitor type.
6. The current status and response time are saved in the database.
7. Historical monitoring data is stored for graphs and logs.
8. The frontend fetches updated monitor data using APIs.
9. Telegram alerts are sent when a service goes down or recovers.
10. The dashboard displays live uptime, response time, and incident details.

---

## Dashboard Features

- Service status cards
- Uptime percentage display
- Response time display
- Search and filtering
- History graphs
- Real-time status updates
- Incident banner
- Health statistics
- Monitor add and delete options
- Clean and responsive UI

---

## Telegram Alerts

PulseGuard integrates with the **Telegram Bot API** to send instant alerts when a monitored service changes its status.

Alerts are sent when:

- A service goes **DOWN**
- A service recovers and comes back **UP**

### Example Down Alert

```text
DOWN Alert

Service: Nginx
Status: DOWN
Response Time: 0 ms
```

### Example Recovery Alert

```text
UP Alert

Service: Nginx
Status: UP
Response Time: 25 ms
```

---

## Docker Deployment

PulseGuard runs inside Docker containers, making it easy to deploy and test across different systems.

### Services Used

- PulseGuard Application
- Nginx Test Container
- Apache Test Container
- Redis Test Container

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ayushx69/pulseguard-Realtime-monitor.git
```

### 2. Move into the Project Directory

```bash
cd pulseguard-Realtime-monitor
```

### 3. Run the Project Using Docker

```bash
docker compose up -d --build
```

---

## Access Application

### PulseGuard Dashboard

```text
http://localhost:5000
```

### Nginx Test Service

```text
http://localhost:8080
```

---

## Default Login Credentials

```text
Username: admin
Password: 1234
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/monitors` | GET | Fetch all monitor data |
| `/add` | POST | Add a new monitor |
| `/delete/<id>` | GET | Delete a monitor |
| `/history/<id>` | GET | View monitor history |

---

## Database Design

PulseGuard uses **SQLite** as a lightweight local database.

---

### Monitors Table

The monitors table stores monitor configuration and latest status information.

It stores:

- Service name
- Target URL or IP address
- Monitor type
- Current status
- Response time
- Last checked time

---

### History Table

The history table stores historical monitoring records.

It stores:

- Monitor ID
- Status
- Response time
- Timestamp
- Monitoring logs
- Status change records

---

## Project Structure

```text
pulseguard-Realtime-monitor/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── database.db
│
├── templates/
│   ├── login.html
│   └── dashboard.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

## Environment Configuration

Telegram alert configuration can be added using environment variables or directly inside the application configuration.

Example:

```text
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## Future Improvements

- Email and SMS alerts
- Multi-user authentication
- Role-based access control
- Cloud database integration
- SSL certificate monitoring
- Domain expiry monitoring
- Mobile application support
- Advanced analytics dashboard
- Export monitoring reports
- More notification integrations

---

## Learning Outcomes

This project helped in understanding:

- Flask backend development
- REST API creation
- Docker containerization
- Docker Compose service management
- SQLite database usage
- Background job scheduling using APScheduler
- HTTP, ICMP, and TCP monitoring concepts
- Telegram Bot API integration
- Real-time dashboard design
- Basic authentication system

---

## Author

**Ayush Sharma**  
System & Network Administrator

---

## GitHub

```text
https://github.com/ayushx69
```

---

## Project Repository

```text
https://github.com/ayushx69/pulseguard-Realtime-monitor
```

---

## License

This project is created for learning and educational purposes.
