# Campus Assistant Chatbot - Backend

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
python chatbot_engine.py
```

6. Run the Flask server:
```bash
python app.py
```

The backend server will start at `http://localhost:5000`

## API Endpoints

### Chat
- **POST** `/api/chat` - Send message to chatbot
  - Body: `{ "message": "your message", "user_id": "optional" }`
  - Response: `{ "response": "bot response", "intent": "detected intent", "confidence": 0.85 }`

### FAQs
- **GET** `/api/faqs` - Get all FAQs (optional: `?category=General`)
- **POST** `/api/faqs` - Add new FAQ (Admin)
  - Body: `{ "category": "General", "question": "...", "answer": "...", "keywords": "..." }`
- **PUT** `/api/faqs/:id` - Update FAQ (Admin)
- **DELETE** `/api/faqs/:id` - Delete FAQ (Admin)

### Analytics
- **GET** `/api/analytics` - Get usage statistics (Admin)

### Health
- **GET** `/api/health` - Check server health

## Database Schema

### chat_logs
- id (PRIMARY KEY)
- user_id
- user_message
- bot_response
- timestamp
- intent
- confidence

### faqs
- id (PRIMARY KEY)
- category
- question
- answer
- keywords
- created_at
- updated_at

### analytics
- id (PRIMARY KEY)
- date
- total_queries
- unique_users
- avg_response_time
- top_intent

## Features

✅ Natural Language Processing for intent detection
✅ Pattern matching with similarity scoring
✅ Dynamic FAQ management
✅ Chat history logging
✅ Analytics and insights
✅ RESTful API design
✅ SQLite database
✅ CORS enabled for frontend integration
