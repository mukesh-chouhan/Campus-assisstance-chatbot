# 🤖 Campus Assistant Chatbot - Frontend

Modern React application with Vite for campus information assistance.

## 🎨 UI Theme
- **Colors**: Black (#000) and Green (#00ff7f)
- **Design**: Modern gradients with smooth animations
- **Responsive**: Works on all devices

## 📁 Project Structure

```
src/
├── page/
│   ├── userlogin.jsx       # Login page with student/admin toggle
│   ├── userPage.jsx        # Student chat interface
│   └── AdminDashboard.jsx  # Admin panel with analytics
├── supabase/
│   └── supabase.js         # Supabase configuration
├── App.jsx                 # Main app with routing
├── main.jsx                # Entry point
└── index.css               # Global styles
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env` file:
```env
VITE_GOOGLE_API_KEY=your_gemini_api_key
VITE_SUPABASE_URL=your_supabase_url (optional)
VITE_SUPABASE_ANON_KEY=your_supabase_key (optional)
```

### 3. Start Development Server
```bash
npm run dev
```

App runs at: `http://localhost:5173`

## 🔧 Available Scripts

- **`npm run dev`** - Start development server with HMR
- **`npm run build`** - Build for production
- **`npm run preview`** - Preview production build
- **`npm run lint`** - Run ESLint

## 📦 Dependencies

- **React 19.1** - UI library
- **React Router 7.8** - Routing
- **React Icons** - Icon library
- **Supabase** - Authentication
- **Bootstrap 5.3** - UI components (optional)
- **Vite 7.0** - Build tool

## 🎯 Features

### Student Interface
- Real-time chat with AI bot
- Message history with timestamps
- Typing indicators
- Suggested questions
- Intent confidence display
- Auto-scroll to latest message

### Admin Dashboard
- Analytics overview
- FAQ management (CRUD)
- Chat logs viewer
- Visual charts and graphs
- Real-time statistics

### Login System
- Dual mode (Student/Admin)
- Email validation
- Password visibility toggle
- Error handling
- Success feedback

## 🔌 Backend Integration

Connects to Flask backend at `http://localhost:5000`

### API Endpoints Used:
- `POST /api/chat` - Send messages
- `GET /api/faqs` - Fetch FAQs
- `POST /api/faqs` - Add FAQ (admin)
- `PUT /api/faqs/:id` - Update FAQ (admin)
- `DELETE /api/faqs/:id` - Delete FAQ (admin)
- `GET /api/analytics` - Get statistics (admin)

## 🎨 Styling

- **Inline CSS** with React components
- **Gradients** for modern look
- **Animations** for smooth UX
- **Custom scrollbars** with green theme
- **Responsive** breakpoints

## 🔐 Demo Credentials

**Admin Login:**
- Email: `admin@iare.ac.in`
- Password: `admin123`

**Student Login:**
- Use Supabase auth or modify code to bypass

## 📱 Routes

- `/` - Login page
- `/user` - Student chat interface
- `/admin` - Admin dashboard

## 🛠️ Tech Stack

- **Vite** - Fast development and HMR
- **React** - Component-based UI
- **React Router** - Client-side routing
- **Fetch API** - HTTP requests
- **LocalStorage** - Session management

## 🐛 Troubleshooting

**Blank page:**
- Check browser console (F12)
- Verify backend is running
- Check .env file exists

**CORS errors:**
- Backend must have Flask-CORS enabled
- Backend should run on port 5000

**Build fails:**
- Clear node_modules: `rm -rf node_modules`
- Reinstall: `npm install`

## 📚 Learn More

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [React Router](https://reactrouter.com)
- [Supabase Docs](https://supabase.com/docs)

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy Options
- **Vercel** (Recommended)
- **Netlify**
- **GitHub Pages**
- **Firebase Hosting**

---

Built with ❤️ using React + Vite
