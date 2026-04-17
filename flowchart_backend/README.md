# FlowDrop — Visual Dropdown Flow Builder

A real-time collaborative canvas-based flowchart tool for building interactive dropdown flows (like the LFP battery selection chart in your notes).

## Features
- 🎨 Canvas-based drag-and-drop node editor
- 📦 Dropdown nodes with multiple options
- 🔗 Connect option outputs to child nodes (cascading dropdowns)
- 👥 Real-time multi-user collaboration (Figma-style cursors with names)
- 💾 Auto-save with Django backend
- 🔐 Simple username/password login
- 🔗 Share via link or specific username
- ▷ Preview mode — test your dropdown flow interactively
- 🗂 Dashboard to manage all your charts

## Quick Start

### 1. Install dependencies
```bash
pip install django django-cors-headers channels daphne
```

### 2. Start the server
```bash
cd flowchart_backend
python run.py
# OR
daphne -p 8000 flowchart_backend.asgi:application
```

### 3. Open in browser
```
http://localhost:8000
```

## How to Use

1. **Register/Login** — Create an account
2. **Create a chart** — Click "New Chart" on dashboard
3. **Add nodes** — Click "+ Dropdown Node" in sidebar or double-click canvas
4. **Edit a node** — Click it to open the panel on the right
   - Set the question/label
   - Add/remove options
   - Add a note (shown in preview)
5. **Connect nodes** — Drag from the dot on the right of any option → to the top dot of another node
6. **Collaborate** — Share the chart URL; collaborators' cursors appear with their names
7. **Preview** — Click ▷ to test the interactive dropdown flow

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register/ | Create account |
| POST | /api/auth/login/ | Sign in |
| POST | /api/auth/logout/ | Sign out |
| GET | /api/auth/me/ | Current user |
| GET/POST | /api/charts/ | List / create charts |
| GET/PUT/DELETE | /api/charts/<id>/ | Get / update / delete chart |
| GET/POST | /api/charts/<id>/share/ | List shares / create share |
| GET | /api/share/<token>/ | Access shared chart |
| GET | /api/users/search/?q=<query> | Search users |

## WebSocket

Real-time events at `ws://localhost:8000/ws/chart/<chart_id>/`

Messages: `join`, `cursor_move`, `canvas_change`, `node_select`

## Database Schema

- **User** — id, username, password_hash, email, avatar_color, created_at, last_login
- **Session** — token, user, created_at, expires_at, is_active
- **FlowChart** — id, title, owner, canvas_data (JSON), created_at, updated_at, is_deleted
- **ChartShare** — id, chart, shared_by, shared_with, share_token, permission, shared_at, accessed_count
- **ChartActivity** — chart, user, action, detail, timestamp
