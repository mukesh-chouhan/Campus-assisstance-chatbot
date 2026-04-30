import React, { useState, useEffect, useRef } from "react";
import { FaSignOutAlt, FaRobot, FaUser, FaPaperPlane, FaLightbulb } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

export default function UserDashboard() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState([
    'Admission process',
    'Placement statistics',
    'Hostel facilities',
    'Library hours'
  ]);
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  const apiKey = import.meta.env.VITE_GEMINI_API_KEY || import.meta.env.VITE_GOOGLE_API_KEY;
  const BACKEND_URL = 'http://localhost:5000';

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Welcome message on load
  useEffect(() => {
    const welcomeMsg = {
      text: "👋 Hello! I'm your Campus Assistant AI. I can help you with information about:\n\n• Admissions & Applications\n• Placements & Careers\n• Hostel & Accommodation\n• Exams & Results\n• Library & Resources\n• Events & Activities\n• Fees & Scholarships\n\nWhat would you like to know?",
      sender: "ai",
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages([welcomeMsg]);
  }, []);

  const handleSend = async (messageText = input) => {
    if (messageText.trim() === "") return;

    // Add user's message to chat
    const userMsg = { 
      text: messageText, 
      sender: "user",
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      // Use local Flask backend with campus-specific knowledge and staff lookup
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: messageText,
          user_id: JSON.parse(localStorage.getItem('user') || '{}').user_id || '23951A62B0'
        }),
      });

      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }

      const data = await res.json();
      const aiMsg = {
        text: data.response,
        sender: "ai",
        timestamp: new Date().toLocaleTimeString(),
        intent: data.intent,
        confidence: data.confidence
      };
      setMessages(prev => [...prev, aiMsg]);
      
      // Update suggestions if provided by backend
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error("Backend Error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          text: "⚠️ Unable to connect to the chatbot backend. Please ensure:\n1. Flask server is running (python app.py)\n2. Backend is accessible at http://localhost:5000\n3. Check the terminal for any errors", 
          sender: "ai",
          timestamp: new Date().toLocaleTimeString()
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSend(suggestion);
  };

  // Format markdown text (bold, line breaks, links, etc.)
  const formatMessage = (text) => {
    if (!text) return text;
    
    // Step 1: Convert **text** to bold
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Step 2: Convert markdown links [text](url) to clickable links that open in new tab
    // This must be done BEFORE plain URL conversion to avoid double-processing
    formatted = formatted.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="message-link">$1</a>'
    );
    
    // Step 3: Convert plain URLs to clickable links (only if not already in a link tag)
    // Use a placeholder to protect already-converted links
    const linkPlaceholder = '___LINK_PROTECTED___';
    const links = [];
    
    // Temporarily replace <a> tags with placeholders
    formatted = formatted.replace(/<a [^>]+>.*?<\/a>/g, (match) => {
      links.push(match);
      return linkPlaceholder;
    });
    
    // Now convert plain URLs
    formatted = formatted.replace(
      /(https?:\/\/[^\s<]+)/g, 
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="message-link">$1</a>'
    );
    formatted = formatted.replace(
      /(www\.[^\s<]+)/g, 
      '<a href="http://$1" target="_blank" rel="noopener noreferrer" class="message-link">$1</a>'
    );
    
    // Restore the protected links
    links.forEach((link) => {
      formatted = formatted.replace(linkPlaceholder, link);
    });
    
    // Step 4: Convert line breaks to <br>
    formatted = formatted.replace(/\n/g, '<br />');
    
    // Step 5: Convert bullet points • to styled bullets
    formatted = formatted.replace(/•/g, '<span class="bullet">•</span>');
    
    // Step 6: Style numbered emojis (1️⃣, 2️⃣, etc.)
    formatted = formatted.replace(/([\d]️⃣)/g, '<span class="emoji-number">$1</span>');
    
    // Step 7: Style other emojis
    formatted = formatted.replace(/(👋|🤖|📚|💡|🎯|✅|🧠|⚡|💬|📊|🚀|😊)/g, '<span class="emoji">$1</span>');
    
    return formatted;
  };

  const handleLogout = () => {
    navigate("/");
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="header-left">
          <FaRobot className="header-icon" />
          <div>
            <div className="title">Campus Assistant AI</div>
            <div className="subtitle">IARE Chatbot - 24/7 Support</div>
          </div>
        </div>
        <button type="button" className="logout-btn" onClick={handleLogout}>
          <FaSignOutAlt /> Logout
        </button>
      </header>

      {/* Messages */}
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.sender}`}>
            <div className="message-avatar">
              {msg.sender === 'user' ? <FaUser /> : <FaRobot />}
            </div>
            <div className="message-bubble">
              <div 
                className="message-content" 
                dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }}
              />
              <div className="message-timestamp">{msg.timestamp}</div>
              {msg.intent && (
                <div className="message-meta">
                  Intent: {msg.intent} | Confidence: {(msg.confidence * 100).toFixed(0)}%
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message-wrapper ai">
            <div className="message-avatar"><FaRobot /></div>
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions-container">
          <FaLightbulb className="suggestions-icon" />
          <div className="suggestions-label">Suggested Questions:</div>
          <div className="suggestions-list">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="input-container">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Ask me anything about campus..."
          className="message-input"
          disabled={isTyping}
        />
        <button 
          onClick={() => handleSend()} 
          className="send-button"
          disabled={!input.trim() || isTyping}
        >
          <FaPaperPlane />
        </button>
      </div>

      {/* Styles */}
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body, #root { height: 100%; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; width: 100%; }
        
        .chat-container { 
          display: flex; 
          flex-direction: column; 
          height: 100vh; 
          background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }
        
        .chat-header { 
          background: linear-gradient(90deg, #000 0%, #1a1a1a 100%);
          color: #00ff7f; 
          padding: 18px 24px; 
          display: flex; 
          justify-content: space-between; 
          align-items: center; 
          border-bottom: 2px solid #00ff7f;
          box-shadow: 0 2px 10px rgba(0, 255, 127, 0.2);
        }
        
        .header-left {
          display: flex;
          align-items: center;
          gap: 15px;
        }
        
        .header-icon {
          font-size: 2rem;
          color: #00ff7f;
          animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        
        .title { 
          font-size: 1.4rem; 
          font-weight: 700;
          letter-spacing: 0.5px;
        }
        
        .subtitle {
          font-size: 0.85rem;
          color: #aaa;
          margin-top: 2px;
        }
        
        .logout-btn { 
          background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
          color: white; 
          border: none; 
          padding: 10px 20px; 
          border-radius: 8px; 
          cursor: pointer; 
          font-size: 0.95rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s ease;
        }
        
        .logout-btn:hover { 
          background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
        }
        
        .messages-container { 
          flex: 1; 
          overflow-y: auto; 
          padding: 24px; 
          display: flex; 
          flex-direction: column; 
          gap: 20px; 
          background: #0f0f0f;
        }
        
        .message-wrapper {
          display: flex;
          gap: 12px;
          animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .message-wrapper.user {
          flex-direction: row-reverse;
        }
        
        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          flex-shrink: 0;
        }
        
        .message-wrapper.user .message-avatar {
          background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%);
          color: #000;
        }
        
        .message-wrapper.ai .message-avatar {
          background: linear-gradient(135deg, #404040 0%, #2a2a2a 100%);
          color: #00ff7f;
        }
        
        .message-bubble {
          max-width: 70%;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        
        .message-content { 
          padding: 14px 18px; 
          border-radius: 16px; 
          font-size: 0.95rem; 
          line-height: 1.6;
          word-wrap: break-word;
        }
        
        .message-content strong {
          font-weight: 700;
          color: #00ff7f;
        }
        
        .message-wrapper.user .message-content strong {
          color: #000;
          font-weight: 800;
        }
        
        .message-content .bullet {
          color: #00ff7f;
          margin-right: 8px;
          font-weight: bold;
        }
        
        .message-content .emoji {
          font-size: 1.1em;
          vertical-align: middle;
        }
        
        .message-content .emoji-number {
          font-size: 1.2em;
          margin-right: 6px;
        }
        
        .message-link {
          color: #00ff7f;
          text-decoration: underline;
          font-weight: 600;
          transition: all 0.3s ease;
          cursor: pointer;
        }
        
        .message-link:hover {
          color: #00e068;
          text-decoration: none;
          text-shadow: 0 0 8px rgba(0, 255, 127, 0.5);
        }
        
        .message-wrapper.user .message-link {
          color: #000;
          font-weight: 700;
        }
        
        .message-wrapper.user .message-link:hover {
          color: #1a1a1a;
          text-shadow: none;
        }
        
        .message-wrapper.user .message-content { 
          background: linear-gradient(135deg, #00ff7f 0%, #00e068 100%);
          color: #000; 
          border-bottom-right-radius: 4px;
          font-weight: 500;
        }
        
        .message-wrapper.ai .message-content { 
          background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
          color: #e0e0e0; 
          border-bottom-left-radius: 4px;
          border: 1px solid #333;
        }
        
        .message-timestamp {
          font-size: 0.75rem;
          color: #888;
          padding: 0 8px;
        }
        
        .message-wrapper.user .message-timestamp {
          text-align: right;
        }
        
        .message-meta {
          font-size: 0.7rem;
          color: #666;
          padding: 4px 8px;
          background: rgba(0, 255, 127, 0.1);
          border-radius: 4px;
          display: inline-block;
        }
        
        .typing-indicator {
          background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
          padding: 14px 20px;
          border-radius: 16px;
          border-bottom-left-radius: 4px;
          display: flex;
          gap: 6px;
          border: 1px solid #333;
        }
        
        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: #00ff7f;
          border-radius: 50%;
          animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
          30% { transform: translateY(-10px); opacity: 1; }
        }
        
        .suggestions-container {
          padding: 12px 24px;
          background: #1a1a1a;
          border-top: 1px solid #2a2a2a;
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }
        
        .suggestions-icon {
          color: #00ff7f;
          font-size: 1.1rem;
        }
        
        .suggestions-label {
          color: #aaa;
          font-size: 0.85rem;
          font-weight: 600;
        }
        
        .suggestions-list {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          flex: 1;
        }
        
        .suggestion-chip {
          padding: 6px 14px;
          background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
          color: #00ff7f;
          border: 1px solid #00ff7f;
          border-radius: 20px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.3s ease;
          white-space: nowrap;
        }
        
        .suggestion-chip:hover {
          background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%);
          color: #000;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 255, 127, 0.3);
        }
        
        .input-container { 
          display: flex; 
          padding: 20px 24px; 
          gap: 12px; 
          background: #000;
          border-top: 2px solid #00ff7f;
        }
        
        .message-input { 
          flex: 1; 
          padding: 14px 20px; 
          border: 2px solid #2a2a2a; 
          border-radius: 25px; 
          background: #1a1a1a;
          color: white; 
          font-size: 1rem; 
          outline: none;
          transition: all 0.3s ease;
        }
        
        .message-input::placeholder { color: #666; }
        
        .message-input:focus { 
          border-color: #00ff7f; 
          box-shadow: 0 0 0 3px rgba(0, 255, 127, 0.2);
          background: #222;
        }
        
        .message-input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .send-button { 
          width: 52px; 
          height: 52px; 
          border: none; 
          border-radius: 50%; 
          background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%);
          color: #000; 
          font-size: 1.1rem; 
          cursor: pointer; 
          display: flex; 
          align-items: center; 
          justify-content: center;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(0, 255, 127, 0.3);
        }
        
        .send-button:hover:not(:disabled) { 
          background: linear-gradient(135deg, #00e068 0%, #00b359 100%);
          transform: scale(1.05) rotate(15deg);
          box-shadow: 0 6px 20px rgba(0, 255, 127, 0.5);
        }
        
        .send-button:disabled {
          opacity: 0.4;
          cursor: not-allowed;
          transform: none;
        }
        
        .messages-container::-webkit-scrollbar { width: 8px; }
        .messages-container::-webkit-scrollbar-track { background: #1a1a1a; }
        .messages-container::-webkit-scrollbar-thumb { 
          background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%);
          border-radius: 4px; 
        }
        .messages-container::-webkit-scrollbar-thumb:hover { background: #00e068; }
      `}</style>
    </div>
  );
}
