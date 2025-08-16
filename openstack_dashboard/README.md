# 🚀 OpenStack Web Dashboard

A modern web interface for OpenStack management, similar to Lens for Kubernetes. Built with React, TypeScript, and OpenStack APIs.

## ✨ Features

- **Resource Management**: Instances, Networks, Volumes, Images
- **Real-time Monitoring**: CPU, Memory, Network usage
- **User Management**: Projects, Users, Roles
- **Network Visualization**: Network topology and security groups
- **Storage Management**: Block storage and object storage
- **Modern UI**: Responsive design with Material-UI

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Material-UI
- **Backend**: Python Flask + OpenStack SDK
- **Authentication**: OpenStack Keystone integration
- **Real-time**: WebSocket for live updates

## 🚀 Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start development servers
npm run dev          # Frontend
python app.py        # Backend
```

## 📋 Requirements

- Node.js 16+
- Python 3.8+
- OpenStack environment
- Modern web browser
