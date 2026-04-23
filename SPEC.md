# Burme AI App - Specification Document

## Project Overview

**Project Name:** Burme AI  
**Project Type:** Flask Web Application for Vercel Deployment  
**Core Functionality:** Multi-provider AI API rotation engine with admin dashboard and user management  
**Target Users:** AI developers and administrators needing high-availability AI chat API

---

## 1. UI/UX Specification

### Layout Structure

**Desktop (≥992px):**
- Sidebar navigation (collapsible, 260px width)
- Main content area with header
- Fixed hamburger button (top-left) to toggle sidebar

**Mobile (<992px):**
- Fixed bottom navigation bar (56px height)
- 5 icon links: Home, Chat, Dashboard, Status, Docs
- No sidebar

**Page Sections:**
- Header: 60px height with logo and hamburger
- Sidebar/Bottom Nav: Navigation menu
- Main Content: Dynamic page content
- Footer: Minimal, 40px

### Responsive Breakpoints
- Mobile: < 576px
- Tablet: 576px - 991px
- Desktop: ≥ 992px

### Visual Design

**Color Palette:**
- Primary: `#0D0D0D` (Deep Black)
- Secondary: `#1A1A2E` (Dark Navy)
- Accent: `#E94560` (Crimson Rose)
- Accent Secondary: `#533483` (Royal Purple)
- Text Primary: `#EAEAEA` (Off White)
- Text Secondary: `#A0A0A0` (Gray)
- Success: `#00D9A5` (Mint Green)
- Warning: `#FFB830` (Amber)
- Error: `#FF4757` (Red)
- Card Background: `#16161A` (Charcoal)
- Input Background: `#1E1E24` (Dark Gray)

**Typography:**
- Font Family: `'Outfit', sans-serif` (Headings), `'DM Sans', sans-serif` (Body)
- Heading 1: 32px, font-weight 700
- Heading 2: 24px, font-weight 600
- Heading 3: 18px, font-weight 600
- Body: 15px, font-weight 400
- Small: 13px, font-weight 400

**Spacing System:**
- Base unit: 8px
- XS: 4px, SM: 8px, MD: 16px, LG: 24px, XL: 32px, XXL: 48px

**Visual Effects:**
- Card shadows: `0 4px 24px rgba(233, 69, 96, 0.08)`
- Hover shadows: `0 8px 32px rgba(233, 69, 96, 0.15)`
- Border radius: 12px (cards), 8px (buttons), 6px (inputs)
- Transitions: 0.3s cubic-bezier(0.4, 0, 0.2, 1)

### Components

**Buttons:**
- Size: `btn-sm` (small)
- Font size: 13px
- Padding: 8px 16px
- Border radius: 8px
- Three.js 3D tilt effect on hover (rotateX: 5deg, rotateY: 5deg)
- Particle emission on click (subtle particle burst)
- Ripple effect on click

**Navigation Items:**
- Icon + Label format
- Font-Awesome icons (NO EMOJIS)
- Active state: Accent color highlight
- Hover: Subtle background change

**Cards:**
- Background: Card Background color
- Border: 1px solid rgba(233, 69, 96, 0.1)
- Padding: 24px
- Border radius: 12px

**Forms:**
- Input background: Input Background
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Focus border: Accent color
- Placeholder color: Text Secondary

**Tables:**
- Striped rows with alternating backgrounds
- Hover row highlight
- Sortable headers

---

## 2. Functionality Specification

### Core Features

#### 2.1 API Rotation Engine

**Providers (in failover order):**
1. Groq
2. Cerebras
3. OpenRouter
4. NVIDIA
5. HuggingFace

**Configuration:**
- Each provider has multiple API keys from environment variables
- Provider order: Groq → Cerebras → OpenRouter → NVIDIA → HuggingFace
- Automatic failover on: rate limit (429), server error (500-599), auth error (401/403)

**Request Flow:**
1. Try first provider's first key
2. If error, try same provider's next key
3. If all keys for provider exhausted, move to next provider
4. Log all attempts with provider/key info
5. Return successful response or final error

**Environment Variables:**
- `GROQ_API_KEY` (supports comma-separated multiple keys)
- `CEREBRAS_API_KEY`
- `OPENROUTER_API_KEY`
- `NVIDIA_API_KEY`
- `HUGGINGFACE_API_KEY`

#### 2.2 Authentication & Security

**data.json Structure:**
```json
{
  "admin": {
    "username": "admin",
    "password_hash": "<bcrypt-hash>"
  },
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "password_hash": "<bcrypt-hash>",
      "created_at": "ISO8601",
      "active": true
    }
  ],
  "logs": [
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "action": "string",
      "user": "string",
      "details": "string"
    }
  ]
}
```

**Login Flow:**
1. POST to `/login` with username/password
2. Validate against data.json
3. Create session with secure cookie
4. Log login attempt
5. Redirect to dashboard or chat

**Session:**
- Flask signed session cookies
- 24-hour expiry
- Secure, HttpOnly flags

#### 2.3 Dashboard Management

**User Management:**
- List all users with pagination
- Add new user (username, password)
- Edit user (username, password, active status)
- Delete user (soft delete by setting active=false)
- Search/filter users

**Activity Logs:**
- View all logged actions
- Filter by user, action type, date range
- Export logs (JSON format)
- Clear old logs (optional)

#### 2.4 API Status Page

**Display:**
- List all 5 providers
- Show status: Active/Inactive/Error
- Show last success timestamp
- Show failure count
- Manual test buttons per provider

#### 2.5 Chat Interface

**Features:**
- Text input for messages
- Markdown rendering support
- Chat history display
- Model selection dropdown
- Clear chat button
- Copy message button

### User Interactions and Flows

**Login Flow:**
1. User visits `/`
2. Enters credentials
3. On success → redirect to `/chat`
4. On failure → show error, stay on page

**Chat Flow:**
1. User enters message
2. Press Enter or click Send
3. Message appears in chat
4. AI response streams in
5. Both messages stored in session

**Dashboard Flow:**
1. Admin clicks Dashboard in nav
2. If not logged in → redirect to `/`
3. Show user management table
4. Show logs table below

---

## 3. Technical Specification

### File Structure
```
/workspace/project/246/
├── api/
│   └── index.py          # Flask app for Vercel
├── static/
│   ├── css/
│   │   └── styles.css  # Custom styles
│   ├── js/
│   │   ├── main.js     # Main JavaScript
│   │   └── three-effects.js  # Three.js button effects
│   └── images/
├── templates/
│   ├── base.html       # Base template
│   ├── login.html      # Get Started / Login
│   ├── chat.html       # Chat interface
│   ├── dashboard.html  # Dashboard
│   ├── status.html     # API Status
│   ├── docs.html       # Documentation
│   └── about.html      # About page
├── data.json           # Storage file
├── vercel.json         # Vercel config
├── requirements.txt    # Python dependencies
└── SPEC.md            # This file
```

### Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Login page |
| `/login` | POST | Process login |
| `/logout` | GET | Clear session |
| `/chat` | GET/POST | Chat interface |
| `/api/chat` | POST | AI chat API |
| `/dashboard` | GET | User & log management |
| `/api/users` | GET/POST/PUT/DELETE | User CRUD |
| `/api/logs` | GET | Get logs |
| `/api-status` | GET | Provider status page |
| `/api/test-provider` | POST | Test single provider |
| `/docs` | GET | Documentation |
| `/about` | GET | About page |

### Dependencies
- Flask>=2.3.0
- flask-cors
- bcrypt
- markdown
- requests

---

## 4. Acceptance Criteria

### Visual Checkpoints
- [ ] Login page displays centered card with form
- [ ] Buttons have Three.js 3D tilt effect on hover
- [ ] Desktop shows collapsible sidebar
- [ ] Mobile shows fixed bottom navigation
- [ ] Chat messages render markdown
- [ ] Dashboard shows user table and logs
- [ ] All icons are Font-Awesome (no emojis)
- [ ] Colors match specification exactly

### Functional Checkpoints
- [ ] Login validates against data.json
- [ ] API rotation tries providers in order
- [ ] Rate limiting triggers failover
- [ ] Failover logs to data.json
- [ ] User CRUD operations work
- [ ] Session persists across requests
- [ ] Vercel deployment works

### Security Checkpoints
- [ ] Passwords hashed with bcrypt
- [ ] Sessions use secure cookies
- [ ] API keys not exposed in responses
- [ ] Input validation on all forms
- [ ] Error messages don't leak info