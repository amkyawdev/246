# 🧠 Burme AI

<p align="center">
  <img src="https://img.shields.io/badge/Burme-AI-E94560?style=for-the-badge&logo=brain&logoColor=white" alt="Burme AI">
  <img src="https://img.shields.io/badge/Python-Flask-000000?style=for-the-badge&logo=python" alt="Flask">
  <img src="https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel" alt="Vercel">
</p>

> **Multi-Provider AI API Platform** with automatic failover, admin dashboard, and high-end UI/UX

## 📸 Preview

<p align="center">
  <img src="https://placehold.co/800x450/0D0D0D/E94560?text=Burme+AI+Chat+Interface" alt="Burme AI Screenshot">
</p>

## 🔗 Live Demo

🌐 **Live Demo**: [https://246-two.vercel.app](https://246-two.vercel.app)

## 📋 Overview

Burme AI is a professional Flask web application designed for Vercel serverless deployment. It provides a high-availability AI chat API that automatically rotates between multiple providers (Groq, Cerebras, OpenRouter, NVIDIA, HuggingFace) with intelligent failover handling.

## ✨ Features

### 🔄 API Rotation Engine
- **5 AI Providers**: Groq, Cerebras, OpenRouter, NVIDIA, HuggingFace
- **Automatic Failover**: Silently switches providers on rate limits (429), server errors (500+), or auth failures
- **Multi-Key Support**: Configure multiple API keys per provider (comma-separated)
- **Real-time Status**: Monitor provider health with live status dashboard

### 🔐 Security
- **BCrypt Password Hashing**: Secure password storage
- **Session-based Authentication**: Secure session cookies with 24-hour expiry
- **Admin Portal**: Dedicated admin login for user management
- **Activity Logging**: Complete audit trail of all actions

### 🎨 UI/UX
- **Bootstrap 5** + **Tailwind CSS** for responsive design
- **Font Awesome Icons** (no emojis)
- **Three.js 3D Effects**: Interactive button tilt and particle effects
- **Responsive Layout**:
  - Desktop: Collapsible sidebar navigation
  - Mobile: Fixed bottom navigation bar

### 📊 Dashboard
- User management (Add/Edit/Delete)
- Activity logs viewer
- API status monitoring
- Export functionality

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/amkyawdev/246.git
cd 246
pip install -r requirements.txt
```

### 2. Configure Environment

Set the following environment variables in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key(s) |
| `CEREBRAS_API_KEY` | Cerebras API key(s) |
| `OPENROUTER_API_KEY` | OpenRouter API key(s) |
| `NVIDIA_API_KEY` | NVIDIA API key(s) |
| `HUGGINGFACE_API_KEY` | HuggingFace API key(s) |
| `SECRET_KEY` | Flask secret key (generate random) |

### 3. Deploy to Vercel

**Option A: Vercel CLI**
```bash
npm i -g vercel
vercel login
vercel --prod
```

**Option B: GitHub Integration**
1. Go to [Vercel Dashboard](https://vercel.com)
2. Import GitHub repository `amkyawdev/246`
3. Add environment variables
4. Deploy!

### 4. Access the App

After deployment, visit your Vercel URL and login with:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| User | `demo` | `user123` |

## 📁 Project Structure

```
burme-ai/
├── api/
│   └── index.py          # Flask application
├── static/
│   ├── css/styles.css   # Custom styles
│   └── js/
│       ├── main.js          # Navigation & utilities
│       └── three-effects.js # 3D button effects
├── templates/
│   ├── base.html       # Base template
│   ├── login.html      # Get Started / Login
│   ├── chat.html       # Chat interface
│   ├── dashboard.html  # User management
│   ├── status.html     # API status
│   ├── docs.html       # Documentation
│   └── about.html      # About page
├── data.json           # User data & logs
├── vercel.json         # Vercel config
├── requirements.txt    # Python dependencies
└── README.md         # This file
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Login page |
| `/login` | POST | Authenticate |
| `/chat` | GET/POST | Chat interface |
| `/api/chat` | POST | AI chat API |
| `/dashboard` | GET | Admin dashboard |
| `/api/users` | CRUD | User management |
| `/api/logs` | GET | Activity logs |
| `/api-status` | GET | Provider status |
| `/api/test-provider` | POST | Test provider |
| `/docs` | GET | Documentation |
| `/about` | GET | About page |

## 💬 Chat API Usage

```bash
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "history": []
  }'
```

Response:
```json
{
  "success": true,
  "provider": "Groq",
  "response": "Hello! I'm doing well..."
}
```

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| User | `demo` | `user123` |

> ⚠️ **Change default passwords in production!**

## 🎯 Tech Stack

- **Backend**: Python 3.9 + Flask 2.3
- **Security**: BCrypt 4.1
- **Frontend**: Bootstrap 5.3 + Tailwind CSS 2.2
- **3D Effects**: Three.js r128
- **Icons**: Font Awesome 6.5
- **PWA**: Service Worker + Web App Manifest
- **Deployment**: Vercel Serverless

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/amkyawdev">amkyawdev</a></sub>
</p>