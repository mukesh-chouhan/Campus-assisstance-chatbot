import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FaChartLine, FaUsers, FaComments, FaQuestionCircle, 
  FaPlus, FaEdit, FaTrash, FaSignOutAlt, FaRobot,
  FaCalendarAlt, FaTrophy
} from 'react-icons/fa';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('analytics');
  const [analytics, setAnalytics] = useState(null);
  const [faqs, setFaqs] = useState([]);
  const [users, setUsers] = useState([]);
  const [newFaq, setNewFaq] = useState({
    category: 'General',
    question: '',
    answer: '',
    keywords: ''
  });
  const [editingFaq, setEditingFaq] = useState(null);
  const navigate = useNavigate();
  const BACKEND_URL = 'http://localhost:5000';

  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalytics();
    } else if (activeTab === 'faqs') {
      fetchFaqs();
    } else if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/analytics`);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchFaqs = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/faqs`);
      if (res.ok) {
        const data = await res.json();
        setFaqs(data);
      }
    } catch (error) {
      console.error('Error fetching FAQs:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/users`);
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleAddFaq = async () => {
    if (!newFaq.question || !newFaq.answer) {
      alert('Question and Answer are required!');
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/api/faqs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newFaq)
      });

      if (res.ok) {
        alert('FAQ added successfully!');
        setNewFaq({ category: 'General', question: '', answer: '', keywords: '' });
        fetchFaqs();
      }
    } catch (error) {
      console.error('Error adding FAQ:', error);
      alert('Error adding FAQ. Make sure backend is running.');
    }
  };

  const handleUpdateFaq = async () => {
    if (!editingFaq) return;

    try {
      const res = await fetch(`${BACKEND_URL}/api/faqs/${editingFaq.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingFaq)
      });

      if (res.ok) {
        alert('FAQ updated successfully!');
        setEditingFaq(null);
        fetchFaqs();
      }
    } catch (error) {
      console.error('Error updating FAQ:', error);
    }
  };

  const handleDeleteFaq = async (id) => {
    if (!confirm('Are you sure you want to delete this FAQ?')) return;

    try {
      const res = await fetch(`${BACKEND_URL}/api/faqs/${id}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        alert('FAQ deleted successfully!');
        fetchFaqs();
      }
    } catch (error) {
      console.error('Error deleting FAQ:', error);
    }
  };

  const handleLogout = () => {
    navigate('/');
  };

  return (
    <div className="admin-container">
      {/* Header */}
      <header className="admin-header">
        <div className="header-left">
          <FaRobot className="header-icon" />
          <div>
            <div className="title">Admin Dashboard</div>
            <div className="subtitle">Campus Assistant Management</div>
          </div>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          <FaSignOutAlt /> Logout
        </button>
      </header>

      {/* Navigation Tabs */}
      <div className="nav-tabs">
        <button
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <FaChartLine /> Analytics
        </button>
        <button
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <FaUsers /> Users
        </button>
        <button
          className={`tab ${activeTab === 'faqs' ? 'active' : ''}`}
          onClick={() => setActiveTab('faqs')}
        >
          <FaQuestionCircle /> Manage FAQs
        </button>
        <button
          className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          <FaComments /> Chat Logs
        </button>
      </div>

      {/* Content Area */}
      <div className="admin-content">
        {activeTab === 'analytics' && (
          <div className="analytics-section">
            <h2>Analytics Overview</h2>
            
            {analytics ? (
              <>
                <div className="stats-grid">
                  <div className="stat-card">
                    <FaComments className="stat-icon" />
                    <div className="stat-value">{analytics.total_queries}</div>
                    <div className="stat-label">Total Queries</div>
                  </div>
                  <div className="stat-card">
                    <FaUsers className="stat-icon" />
                    <div className="stat-value">{analytics.unique_users}</div>
                    <div className="stat-label">Unique Users</div>
                  </div>
                  <div className="stat-card">
                    <FaTrophy className="stat-icon" />
                    <div className="stat-value">
                      {analytics.top_intents[0]?.intent || 'N/A'}
                    </div>
                    <div className="stat-label">Top Intent</div>
                  </div>
                  <div className="stat-card">
                    <FaCalendarAlt className="stat-icon" />
                    <div className="stat-value">
                      {analytics.queries_by_date.length}
                    </div>
                    <div className="stat-label">Active Days</div>
                  </div>
                </div>

                <div className="section-row">
                  <div className="section-box">
                    <h3>Top Intents</h3>
                    <div className="intents-list">
                      {analytics.top_intents.map((intent, idx) => (
                        <div key={idx} className="intent-item">
                          <span className="intent-name">{intent.intent}</span>
                          <span className="intent-count">{intent.count} queries</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="section-box">
                    <h3>Queries by Date (Last 7 Days)</h3>
                    <div className="queries-list">
                      {analytics.queries_by_date.map((item, idx) => (
                        <div key={idx} className="query-date-item">
                          <span className="date">{item.date}</span>
                          <div className="query-bar">
                            <div 
                              className="query-bar-fill" 
                              style={{width: `${(item.count / Math.max(...analytics.queries_by_date.map(q => q.count))) * 100}%`}}
                            />
                            <span className="query-count">{item.count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="section-box full-width">
                  <h3>Recent Queries</h3>
                  <div className="recent-queries">
                    {analytics.recent_queries.slice(0, 10).map((query, idx) => (
                      <div key={idx} className="query-item">
                        <div className="query-text">
                          <strong>Q:</strong> {query.user_message}
                        </div>
                        <div className="query-response">
                          <strong>A:</strong> {query.bot_response.substring(0, 100)}...
                        </div>
                        <div className="query-meta">
                          <span className="query-time">{new Date(query.timestamp).toLocaleString()}</span>
                          <span className="query-intent">{query.intent}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="loading">Loading analytics...</div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-section">
            <h2>Registered Users</h2>
            
            <div className="users-stats">
              <div className="stat-card">
                <FaUsers className="stat-icon" />
                <div className="stat-value">{users.length}</div>
                <div className="stat-label">Total Users</div>
              </div>
              <div className="stat-card">
                <FaUsers className="stat-icon" />
                <div className="stat-value">{users.filter(u => u.role === 'student').length}</div>
                <div className="stat-label">Students</div>
              </div>
              <div className="stat-card">
                <FaUsers className="stat-icon" />
                <div className="stat-value">{users.filter(u => u.role === 'admin').length}</div>
                <div className="stat-label">Admins</div>
              </div>
            </div>

            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>User ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Roll Number</th>
                    <th>Department</th>
                    <th>Year</th>
                    <th>Phone</th>
                    <th>Created At</th>
                    <th>Last Login</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td><span className="user-id">{user.user_id}</span></td>
                      <td><strong>{user.name}</strong></td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`role-badge ${user.role}`}>
                          {user.role}
                        </span>
                      </td>
                      <td>{user.roll_number || 'N/A'}</td>
                      <td>{user.department || 'N/A'}</td>
                      <td>{user.year || 'N/A'}</td>
                      <td>{user.phone || 'N/A'}</td>
                      <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                      <td>{user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                      <td>
                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'faqs' && (
          <div className="faqs-section">
            <h2>FAQ Management</h2>
            
            {/* Add New FAQ */}
            <div className="faq-form">
              <h3><FaPlus /> Add New FAQ</h3>
              <div className="form-grid">
                <select
                  value={newFaq.category}
                  onChange={(e) => setNewFaq({...newFaq, category: e.target.value})}
                  className="form-input"
                >
                  <option>General</option>
                  <option>Admissions</option>
                  <option>Academics</option>
                  <option>Facilities</option>
                  <option>Sports</option>
                  <option>Placements</option>
                  <option>Events</option>
                </select>
                <input
                  type="text"
                  placeholder="Keywords (comma-separated)"
                  value={newFaq.keywords}
                  onChange={(e) => setNewFaq({...newFaq, keywords: e.target.value})}
                  className="form-input"
                />
              </div>
              <input
                type="text"
                placeholder="Question"
                value={newFaq.question}
                onChange={(e) => setNewFaq({...newFaq, question: e.target.value})}
                className="form-input full"
              />
              <textarea
                placeholder="Answer"
                value={newFaq.answer}
                onChange={(e) => setNewFaq({...newFaq, answer: e.target.value})}
                className="form-textarea"
                rows="4"
              />
              <button className="btn-primary" onClick={handleAddFaq}>
                <FaPlus /> Add FAQ
              </button>
            </div>

            {/* Existing FAQs */}
            <div className="faqs-list">
              <h3>Existing FAQs ({faqs.length})</h3>
              {faqs.map((faq) => (
                <div key={faq.id} className="faq-item">
                  {editingFaq?.id === faq.id ? (
                    <div className="faq-edit">
                      <select
                        value={editingFaq.category}
                        onChange={(e) => setEditingFaq({...editingFaq, category: e.target.value})}
                        className="form-input"
                      >
                        <option>General</option>
                        <option>Admissions</option>
                        <option>Academics</option>
                        <option>Facilities</option>
                        <option>Sports</option>
                        <option>Placements</option>
                        <option>Events</option>
                      </select>
                      <input
                        type="text"
                        value={editingFaq.question}
                        onChange={(e) => setEditingFaq({...editingFaq, question: e.target.value})}
                        className="form-input full"
                      />
                      <textarea
                        value={editingFaq.answer}
                        onChange={(e) => setEditingFaq({...editingFaq, answer: e.target.value})}
                        className="form-textarea"
                        rows="3"
                      />
                      <input
                        type="text"
                        placeholder="Keywords"
                        value={editingFaq.keywords}
                        onChange={(e) => setEditingFaq({...editingFaq, keywords: e.target.value})}
                        className="form-input"
                      />
                      <div className="faq-actions">
                        <button className="btn-success" onClick={handleUpdateFaq}>Save</button>
                        <button className="btn-secondary" onClick={() => setEditingFaq(null)}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="faq-header">
                        <span className="faq-category">{faq.category}</span>
                        <div className="faq-actions">
                          <button className="btn-icon" onClick={() => setEditingFaq(faq)}>
                            <FaEdit />
                          </button>
                          <button className="btn-icon delete" onClick={() => handleDeleteFaq(faq.id)}>
                            <FaTrash />
                          </button>
                        </div>
                      </div>
                      <div className="faq-question">{faq.question}</div>
                      <div className="faq-answer">{faq.answer}</div>
                      {faq.keywords && (
                        <div className="faq-keywords">
                          Keywords: {faq.keywords}
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="logs-section">
            <h2>Chat Logs</h2>
            {analytics?.recent_queries ? (
              <div className="logs-list">
                {analytics.recent_queries.map((log, idx) => (
                  <div key={idx} className="log-item">
                    <div className="log-header">
                      <span className="log-time">{new Date(log.timestamp).toLocaleString()}</span>
                      <span className="log-intent">{log.intent}</span>
                    </div>
                    <div className="log-message user">
                      <strong>User:</strong> {log.user_message}
                    </div>
                    <div className="log-message bot">
                      <strong>Bot:</strong> {log.bot_response}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="loading">No logs available</div>
            )}
          </div>
        )}
      </div>

      {/* Styles */}
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        html, body, #root {
          height: 100%;
          width: 100%;
          overflow-x: hidden;
        }
        
        .admin-container {
          min-height: 100vh;
          height: 100%;
          width: 100%;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          color: white;
          font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          display: flex;
          flex-direction: column;
        }

        .admin-header {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 20px 32px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 3px solid #00ff7f;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          position: sticky;
          top: 0;
          z-index: 100;
          backdrop-filter: blur(10px);
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .header-icon {
          font-size: 2.5rem;
          color: #00ff7f;
          animation: pulse 2s infinite;
          filter: drop-shadow(0 0 10px rgba(0, 255, 127, 0.5));
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.05); }
        }

        .title {
          font-size: 1.8rem;
          font-weight: 800;
          color: #ffffff;
          letter-spacing: 0.5px;
          text-shadow: 0 2px 10px rgba(0, 255, 127, 0.3);
        }

        .subtitle {
          font-size: 0.9rem;
          color: #94a3b8;
          margin-top: 2px;
          font-weight: 500;
        }

        .logout-btn {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
          border: none;
          padding: 12px 28px;
          border-radius: 10px;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 10px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }

        .logout-btn:hover {
          background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5);
        }

        .nav-tabs {
          display: flex;
          background: #1e293b;
          border-bottom: 2px solid #334155;
          padding: 0 32px;
          gap: 8px;
          position: sticky;
          top: 76px;
          z-index: 90;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .tab {
          padding: 18px 32px;
          background: transparent;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          font-size: 1.05rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 10px;
          border-bottom: 4px solid transparent;
          transition: all 0.3s ease;
          position: relative;
        }

        .tab:hover {
          color: #00ff7f;
          background: rgba(0, 255, 127, 0.08);
        }

        .tab.active {
          color: #00ff7f;
          border-bottom-color: #00ff7f;
          background: rgba(0, 255, 127, 0.1);
        }

        .tab.active::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 3px;
          background: linear-gradient(90deg, transparent, #00ff7f, transparent);
        }

        .admin-content {
          flex: 1;
          padding: 40px 32px;
          max-width: 1600px;
          width: 100%;
          margin: 0 auto;
          overflow-y: auto;
        }

        .analytics-section, .faqs-section, .logs-section {
          animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        h2 {
          color: #ffffff;
          margin-bottom: 32px;
          font-size: 2.2rem;
          font-weight: 800;
          display: flex;
          align-items: center;
          gap: 16px;
          padding-bottom: 16px;
          border-bottom: 3px solid #334155;
        }

        h2::before {
          content: '';
          width: 6px;
          height: 40px;
          background: linear-gradient(180deg, #00ff7f, #00cc66);
          border-radius: 3px;
        }

        h3 {
          color: #e2e8f0;
          margin-bottom: 20px;
          font-size: 1.4rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 24px;
          margin-bottom: 40px;
        }

        .stat-card {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 32px;
          border-radius: 16px;
          border: 2px solid #334155;
          text-align: center;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          position: relative;
          overflow: hidden;
        }

        .stat-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, #00ff7f, #00cc66);
          transform: scaleX(0);
          transition: transform 0.4s ease;
        }

        .stat-card:hover::before {
          transform: scaleX(1);
        }

        .stat-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 32px rgba(0, 255, 127, 0.25);
          border-color: #00ff7f;
          background: linear-gradient(135deg, #334155 0%, #475569 100%);
        }

        .stat-icon {
          font-size: 3rem;
          color: #00ff7f;
          margin-bottom: 16px;
          filter: drop-shadow(0 0 15px rgba(0, 255, 127, 0.5));
        }

        .stat-value {
          font-size: 3rem;
          font-weight: 900;
          background: linear-gradient(135deg, #00ff7f, #00cc66);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 8px;
          text-shadow: 0 4px 15px rgba(0, 255, 127, 0.3);
        }

        .stat-label {
          color: #cbd5e1;
          font-size: 1rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .section-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
        }

        .section-box {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 28px;
          border-radius: 16px;
          border: 2px solid #334155;
          transition: all 0.3s ease;
        }

        .section-box:hover {
          border-color: #475569;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .section-box.full-width {
          grid-column: 1 / -1;
        }

        .intents-list, .queries-list {
          display: flex;
          flex-direction: column;
          gap: 14px;
        }

        .intent-item {
          display: flex;
          justify-content: space-between;
          padding: 16px 20px;
          background: rgba(15, 23, 42, 0.6);
          border-radius: 10px;
          border-left: 4px solid #00ff7f;
          transition: all 0.3s ease;
        }

        .intent-item:hover {
          background: rgba(15, 23, 42, 0.9);
          transform: translateX(8px);
        }

        .intent-name {
          color: #f1f5f9;
          font-weight: 700;
          font-size: 1.05rem;
        }

        .intent-count {
          background: rgba(0, 255, 127, 0.2);
          color: #00ff7f;
          padding: 4px 14px;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: 700;
        }

        .query-date-item {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 8px 0;
        }

        .date {
          min-width: 120px;
          color: #cbd5e1;
          font-size: 0.95rem;
          font-weight: 600;
        }

        .query-bar {
          flex: 1;
          height: 32px;
          background: rgba(15, 23, 42, 0.6);
          border-radius: 8px;
          position: relative;
          overflow: hidden;
          border: 1px solid #334155;
        }

        .query-bar-fill {
          height: 100%;
          background: linear-gradient(90deg, #00ff7f 0%, #00cc66 100%);
          transition: width 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          box-shadow: 0 0 15px rgba(0, 255, 127, 0.5);
        }

        .query-count {
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: #fff;
          font-weight: 700;
          font-size: 0.9rem;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }

        .recent-queries, .logs-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .query-item, .log-item {
          background: rgba(15, 23, 42, 0.6);
          padding: 20px;
          border-radius: 12px;
          border-left: 4px solid #00ff7f;
          transition: all 0.3s ease;
          border: 1px solid #334155;
        }

        .query-item:hover, .log-item:hover {
          background: rgba(15, 23, 42, 0.9);
          border-color: #00ff7f;
          box-shadow: 0 4px 16px rgba(0, 255, 127, 0.2);
        }

        .query-text, .query-response {
          margin-bottom: 12px;
          line-height: 1.7;
        }

        .query-text {
          color: #f1f5f9;
          font-size: 1.05rem;
        }

        .query-text strong, .query-response strong, .log-message strong {
          color: #00ff7f;
          font-weight: 700;
        }

        .query-response {
          color: #cbd5e1;
          font-size: 0.95rem;
          padding-left: 20px;
          border-left: 2px solid #334155;
        }

        .query-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 2px solid #334155;
        }

        .query-time {
          color: #94a3b8;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .query-intent {
          background: linear-gradient(135deg, rgba(0, 255, 127, 0.2), rgba(0, 204, 102, 0.2));
          color: #00ff7f;
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 700;
          border: 1px solid rgba(0, 255, 127, 0.3);
        }

        .faq-form {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 32px;
          border-radius: 16px;
          margin-bottom: 40px;
          border: 2px solid #334155;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 20px;
        }

        .form-input, .form-textarea {
          width: 100%;
          padding: 14px 18px;
          background: rgba(15, 23, 42, 0.6);
          border: 2px solid #334155;
          border-radius: 10px;
          color: white;
          font-size: 1rem;
          font-family: inherit;
          transition: all 0.3s ease;
          font-weight: 500;
        }

        .form-input::placeholder, .form-textarea::placeholder {
          color: #64748b;
        }

        .form-input.full {
          grid-column: 1 / -1;
          margin-bottom: 20px;
        }

        .form-input:focus, .form-textarea:focus {
          outline: none;
          border-color: #00ff7f;
          background: rgba(15, 23, 42, 0.9);
          box-shadow: 0 0 0 4px rgba(0, 255, 127, 0.1);
        }

        .form-textarea {
          resize: vertical;
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .btn-primary {
          background: linear-gradient(135deg, #00ff7f 0%, #00cc66 100%);
          color: #000;
          border: none;
          padding: 14px 32px;
          border-radius: 10px;
          font-weight: 700;
          font-size: 1.05rem;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 10px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 16px rgba(0, 255, 127, 0.3);
        }

        .btn-primary:hover {
          background: linear-gradient(135deg, #00e068 0%, #00b359 100%);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 255, 127, 0.5);
        }

        .btn-primary:active {
          transform: translateY(0);
        }

        .btn-success, .btn-secondary {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 0.95rem;
        }

        .btn-success {
          background: linear-gradient(135deg, #00ff7f, #00cc66);
          color: #000;
          box-shadow: 0 2px 8px rgba(0, 255, 127, 0.3);
        }

        .btn-success:hover {
          box-shadow: 0 4px 16px rgba(0, 255, 127, 0.5);
          transform: translateY(-2px);
        }

        .btn-secondary {
          background: #64748b;
          color: white;
        }

        .btn-secondary:hover {
          background: #475569;
        }

        .faqs-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .faq-item {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 24px;
          border-radius: 16px;
          border: 2px solid #334155;
          transition: all 0.3s ease;
        }

        .faq-item:hover {
          border-color: #475569;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .faq-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .faq-category {
          background: linear-gradient(135deg, rgba(0, 255, 127, 0.2), rgba(0, 204, 102, 0.2));
          color: #00ff7f;
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: 700;
          border: 1px solid rgba(0, 255, 127, 0.3);
        }

        .faq-actions {
          display: flex;
          gap: 10px;
        }

        .btn-icon {
          background: rgba(15, 23, 42, 0.6);
          border: 2px solid #00ff7f;
          color: #00ff7f;
          width: 40px;
          height: 40px;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          font-size: 1.1rem;
        }

        .btn-icon:hover {
          background: #00ff7f;
          color: #000;
          transform: scale(1.1);
        }

        .btn-icon.delete {
          border-color: #ef4444;
          color: #ef4444;
        }

        .btn-icon.delete:hover {
          background: #ef4444;
          color: white;
        }

        .faq-question {
          font-size: 1.15rem;
          font-weight: 700;
          color: #f1f5f9;
          margin-bottom: 14px;
          line-height: 1.5;
        }

        .faq-answer {
          color: #cbd5e1;
          line-height: 1.7;
          margin-bottom: 14px;
          font-size: 1rem;
        }

        .faq-keywords {
          font-size: 0.9rem;
          color: #94a3b8;
          font-style: italic;
          padding: 8px 12px;
          background: rgba(15, 23, 42, 0.4);
          border-radius: 6px;
          border-left: 3px solid #334155;
        }

        .loading {
          text-align: center;
          padding: 60px 20px;
          color: #94a3b8;
          font-size: 1.3rem;
          font-weight: 600;
        }

        .log-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 2px solid #334155;
        }

        .log-time {
          color: #94a3b8;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .log-intent {
          background: linear-gradient(135deg, rgba(0, 255, 127, 0.2), rgba(0, 204, 102, 0.2));
          color: #00ff7f;
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 700;
          border: 1px solid rgba(0, 255, 127, 0.3);
        }

        .log-message {
          padding: 10px 0;
          line-height: 1.7;
          font-size: 1rem;
        }

        .log-message.user {
          color: #f1f5f9;
        }

        .log-message.bot {
          color: #cbd5e1;
          padding-left: 16px;
          border-left: 2px solid #334155;
        }

        .faq-edit {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        /* Users Section Styles */
        .users-section {
          animation: fadeIn 0.5s ease;
        }

        .users-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 24px;
          margin-bottom: 40px;
        }

        .users-table-container {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 28px;
          border-radius: 16px;
          border: 2px solid #334155;
          overflow-x: auto;
        }

        .users-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.95rem;
        }

        .users-table thead {
          background: rgba(0, 255, 127, 0.1);
          border-bottom: 3px solid #00ff7f;
        }

        .users-table th {
          padding: 16px 12px;
          text-align: left;
          font-weight: 700;
          color: #00ff7f;
          font-size: 0.9rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          white-space: nowrap;
        }

        .users-table tbody tr {
          border-bottom: 1px solid #334155;
          transition: all 0.3s ease;
        }

        .users-table tbody tr:hover {
          background: rgba(0, 255, 127, 0.05);
          transform: scale(1.01);
        }

        .users-table td {
          padding: 16px 12px;
          color: #cbd5e1;
          white-space: nowrap;
        }

        .users-table td strong {
          color: #f1f5f9;
          font-weight: 700;
        }

        .user-id {
          background: rgba(0, 255, 127, 0.15);
          color: #00ff7f;
          padding: 4px 12px;
          border-radius: 6px;
          font-family: 'Courier New', monospace;
          font-weight: 700;
          font-size: 0.85rem;
          border: 1px solid rgba(0, 255, 127, 0.3);
        }

        .role-badge {
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          display: inline-block;
        }

        .role-badge.student {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.2));
          color: #60a5fa;
          border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .role-badge.admin {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
          color: #f87171;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .status-badge {
          padding: 6px 14px;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          display: inline-block;
        }

        .status-badge.active {
          background: linear-gradient(135deg, rgba(0, 255, 127, 0.2), rgba(0, 204, 102, 0.2));
          color: #00ff7f;
          border: 1px solid rgba(0, 255, 127, 0.3);
        }

        .status-badge.inactive {
          background: linear-gradient(135deg, rgba(100, 116, 139, 0.2), rgba(71, 85, 105, 0.2));
          color: #94a3b8;
          border: 1px solid rgba(100, 116, 139, 0.3);
        }

        /* Scrollbar Styling */
        .admin-content::-webkit-scrollbar {
          width: 10px;
        }

        .admin-content::-webkit-scrollbar-track {
          background: #1e293b;
        }

        .admin-content::-webkit-scrollbar-thumb {
          background: linear-gradient(180deg, #00ff7f, #00cc66);
          border-radius: 5px;
        }

        .admin-content::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(180deg, #00e068, #00b359);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .admin-header {
            padding: 16px 20px;
          }

          .title {
            font-size: 1.4rem;
          }

          .nav-tabs {
            padding: 0 20px;
            overflow-x: auto;
          }

          .tab {
            padding: 14px 20px;
            font-size: 0.95rem;
          }

          .admin-content {
            padding: 24px 20px;
          }

          .stats-grid {
            grid-template-columns: 1fr;
          }

          .section-row {
            grid-template-columns: 1fr;
          }

          .form-grid {
            grid-template-columns: 1fr;
          }

          h2 {
            font-size: 1.8rem;
          }
        }
      `}</style>
    </div>
  );
}
