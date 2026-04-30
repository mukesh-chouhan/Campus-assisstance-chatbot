# Campus Assistance ChatBot

A full-stack campus support chatbot for IARE with:
- React + Vite frontend
- Flask backend
- SQLite storage
- NLP intent detection for campus queries
- Admin dashboard for analytics, users, and FAQs

## Project Overview

This project helps students and admins interact with campus information quickly.

### Student features
- Login with IARE email
- Ask campus-related questions in chat
- Get intent/confidence-based responses
- Forgot-password flow with security question
- View marks through backend API support

### Admin features
- Admin login
- View analytics and recent chat logs
- Manage FAQs (create, update, delete)
- View registered users

## Tech Stack

- **Frontend:** React 19, Vite, React Router, React Icons
- **Backend:** Flask, Flask-CORS, python-dotenv
- **Database:** SQLite (`campus_assistant.db`)
- **NLP/Logic:** Custom rule + similarity matching engine in `backend/chatbot_engine.py`

## Project Structure

```text
CampusAssistanceChatBot/
├── backend/
│   ├── app.py
│   ├── chatbot_engine.py
│   ├── requirements.txt
│   ├── test_intent_detection.py
│   └── test_name_extraction.py
├── CampusAssistancechatBot/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       └── page/
│           ├── userlogin.jsx
│           ├── ForgotPassword.jsx
│           ├── userPage.jsx
│           └── AdminDashboard.jsx
├── QUICKSTART.bat
└── README.md
```

## Prerequisites

- Node.js 18+
- npm 9+
- Python 3.8+

## Quick Start (Windows)

From the project root:

```bat
QUICKSTART.bat
```

Choose option `3` for first-time setup, then option `6` to run both servers.

## Manual Setup

### 1) Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 Install dependencies
```bash
pip install -r requirements.txt
python app.py
```

> The backend asks for a startup PIN.
> - You can override it via env variable `SERVER_PIN`

Backend URL: `http://localhost:5000`

### 2) Frontend

In a new terminal:

```bash
cd CampusAssistancechatBot
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## Environment Variables


### Frontend (`CampusAssistancechatBot/.env`)

Optional in current implementation:

```env
VITE_GOOGLE_API_KEY=your_key
VITE_GEMINI_API_KEY=your_key
```

## Demo Credentials

These are seeded in the backend database on first run.
## Main API Endpoints

Base URL: `http://localhost:5000/api`

- `POST /chat` - Send chat message
- `GET /faqs` - List FAQs
- `POST /faqs` - Add FAQ
- `PUT /faqs/:id` - Update FAQ
- `DELETE /faqs/:id` - Delete FAQ
- `GET /analytics` - Analytics data
- `GET /health` - Health check
- `POST /auth/login` - Login
- `POST /auth/register` - Register
- `POST /auth/forgot-password` - Get security question
- `POST /auth/verify-answer` - Verify security answer
- `POST /auth/reset-password` - Reset password
- `GET /marks?user_id=...` - Student marks
- `GET /users` - List users

## Testing

From `backend/`:

```bash
python test_intent_detection.py
python test_name_extraction.py
```

## Notes

- `campus_assistant.db` is created automatically by the backend.
- CORS for `/api/*` is enabled in Flask.
- Frontend currently uses `http://localhost:5000` directly in page components.

## License

This project is licensed under the MIT License. See `LICENSE`.
---

## 📖 Usage

### Student Access

1. **Navigate to Login**: Open `http://localhost:5173`
2. **Select Student Mode**: Click "Student Login" toggle
3. **Enter Credentials**: Use your college email (@iare.ac.in)
4. **Start Chatting**: Ask questions about campus

**Example Questions:**
- "Tell me about the admission process"
- "What are the placement statistics?"
- "Library hours?"
- "How to apply for hostel?"
- "When is the next tech fest?"

### Admin Access

1. **Navigate to Login**: Open `http://localhost:5173`
2. **Select Admin Mode**: Click "Admin Login" toggle
3. **Use Demo Credentials**:
   - Email: `admin@iare.ac.in`
   - Password: `admin123`
4. **Access Dashboard**: Manage FAQs, view analytics, check logs

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Chat with Bot
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Tell me about admissions",
  "user_id": "user123"
}

Response:
{
  "response": "For admissions, you can visit...",
  "intent": "admission",
  "confidence": 0.85,
  "suggestions": ["Placement info", "Hostel facilities"]
}
```

#### 2. Get All FAQs
```http
GET /api/faqs
GET /api/faqs?category=Admissions

Response:
[
  {
    "id": 1,
    "category": "General",
    "question": "What is the college timing?",
    "answer": "College timings are from 9:00 AM to 4:30 PM",
    "keywords": "timing,hours,schedule"
  }
]
```

#### 3. Add New FAQ (Admin)
```http
POST /api/faqs
Content-Type: application/json

{
  "category": "Admissions",
  "question": "What is the application deadline?",
  "answer": "Applications close on June 30th",
  "keywords": "deadline,last date,application"
}

Response:
{
  "id": 6,
  "message": "FAQ added successfully"
}
```

#### 4. Update FAQ (Admin)
```http
PUT /api/faqs/{id}
Content-Type: application/json

{
  "category": "Admissions",
  "question": "Updated question?",
  "answer": "Updated answer",
  "keywords": "updated,keywords"
}

Response:
{
  "message": "FAQ updated successfully"
}
```

#### 5. Delete FAQ (Admin)
```http
DELETE /api/faqs/{id}

Response:
{
  "message": "FAQ deleted successfully"
}
```

#### 6. Get Analytics (Admin)
```http
GET /api/analytics

Response:
{
  "total_queries": 150,
  "unique_users": 45,
  "top_intents": [
    {"intent": "admission", "count": 30},
    {"intent": "placement", "count": 25}
  ],
  "recent_queries": [...],
  "queries_by_date": [...]
}
```

#### 7. Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 👨‍💼 Admin Dashboard

### Analytics Tab
- **Overview Cards**: Total queries, unique users, top intent, active days
- **Top Intents Chart**: Visual representation of most asked topics
- **Query Trends**: Last 7 days query distribution
- **Recent Queries**: Latest 10 conversations with intent tags

### FAQ Management Tab
- **Add New FAQ**: Category, question, answer, keywords input form
- **Existing FAQs**: Categorized list with edit/delete actions
- **Inline Editing**: Click edit to modify FAQ in place
- **Dynamic Updates**: Changes reflect immediately in chatbot

### Chat Logs Tab
- **Conversation History**: All user interactions with timestamps
- **Intent Tracking**: View detected intents for each query
- **User Analysis**: Track query patterns and user behavior

---

## 🎨 UI/UX Highlights

### Color Scheme
- **Primary**: `#00ff7f` (Spring Green)
- **Secondary**: `#00cc66` (Dark Green)
- **Background**: `#000000` to `#1a1a1a` (Black gradient)
- **Text**: `#e0e0e0` (Light Gray)
- **Accents**: Neon green glows and shadows

### Design Elements
- **Gradients**: Smooth color transitions on buttons and cards
- **Animations**: Slide-in messages, pulse effects, hover transforms
- **Shadows**: Neon glow effects on interactive elements
- **Typography**: Segoe UI for modern, clean readability
- **Icons**: React Icons for consistent visual language

### Responsive Features
- **Mobile-First**: Works on all screen sizes
- **Touch-Friendly**: Large tap targets for mobile
- **Flexible Layouts**: Grid and flexbox for adaptation
- **Smooth Scrolling**: Custom scrollbars with green theme

---

## 🔮 Future Enhancements

### Phase 1: Voice Integration
- [ ] Voice input/output for accessibility
- [ ] Speech-to-text for queries
- [ ] Text-to-speech for responses
- [ ] Multi-language support

### Phase 2: Advanced AI
- [ ] Sentiment analysis for user satisfaction
- [ ] Context-aware conversations (multi-turn)
- [ ] Personalized responses based on user history
- [ ] Image recognition for campus maps/documents

### Phase 3: Integration
- [ ] Integration with student academic records
- [ ] LMS (Learning Management System) connectivity
- [ ] Google Calendar integration for events
- [ ] WhatsApp and Telegram bot deployment

### Phase 4: Smart Features
- [ ] Automatic ticket generation for unresolved queries
- [ ] AI summarization of campus notices
- [ ] Predictive analytics for common issues
- [ ] Multi-channel deployment (mobile app)
- [ ] Push notifications for important updates

### Phase 5: Enhanced Admin
- [ ] Role-based access control
- [ ] Advanced analytics dashboard
- [ ] Export reports (PDF, CSV)
- [ ] A/B testing for responses
- [ ] Chatbot training interface

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs
1. Check if the bug already exists in Issues
2. Create a detailed bug report with steps to reproduce
3. Include screenshots if applicable

### Suggesting Features
1. Open an issue with the "enhancement" label
2. Describe the feature and its use case
3. Explain why it would benefit users

### Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Project Type**: Academic Project / Proof of Concept

**Institution**: Institute of Aeronautical Engineering (IARE)

**Domain**: Artificial Intelligence & Web Development

---

## 📞 Support

For issues, questions, or suggestions:

- **Email**: support@iare.ac.in
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/CampusAssistanceChatBot/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/CampusAssistanceChatBot/wiki)

---

## 🙏 Acknowledgments

- **Google Gemini**: AI fallback for complex queries
- **React Icons**: Beautiful icon library
- **Flask**: Lightweight Python web framework
- **Vite**: Fast frontend build tool

---

## 📊 Project Stats

- **Lines of Code**: ~3000+
- **Components**: 3 main pages (Login, User, Admin)
- **API Endpoints**: 7 RESTful endpoints
- **Intent Categories**: 13 predefined intents
- **Database Tables**: 3 (chat_logs, faqs, analytics)

---

<div align="center">

**Made with ❤️ and 🤖 for better campus communication**

⭐ Star this repo if you found it helpful!

</div>
"# Campus-assisstance-chatbot" 
