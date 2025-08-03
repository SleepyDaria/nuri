import React, { useState, useEffect } from 'react';
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Current user context (for demo purposes, in real app would use auth)
let currentUser = null;

function App() {
  const [page, setPage] = useState('home');
  const [users, setUsers] = useState([]);
  const [cities, setCities] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [matches, setMatches] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  
  // Forms state
  const [userForm, setUserForm] = useState({
    username: '', email: '', phone: '', id_document: '', city: ''
  });
  
  const [transactionForm, setTransactionForm] = useState({
    title: '', description: '', amount: '', currency: 'USD',
    from_city: '', to_city: '', recipient_name: '', recipient_details: ''
  });
  
  const [chatInput, setChatInput] = useState('');

  // Load initial data
  useEffect(() => {
    loadCities();
    loadTransactions();
  }, []);

  const loadCities = async () => {
    try {
      const response = await axios.get(`${API}/cities`);
      setCities(response.data.cities);
    } catch (error) {
      console.error('Error loading cities:', error);
    }
  };

  const loadTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const createUser = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/users`, userForm);
      currentUser = response.data;
      alert(`Welcome ${currentUser.username}! You are now registered.`);
      setPage('dashboard');
    } catch (error) {
      alert('Error creating user: ' + error.response?.data?.detail);
    }
  };

  const createTransaction = async (e) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Please register first');
      return;
    }
    
    try {
      await axios.post(`${API}/transactions?user_id=${currentUser.id}`, transactionForm);
      alert('Transaction posted successfully!');
      loadTransactions();
      setTransactionForm({
        title: '', description: '', amount: '', currency: 'USD',
        from_city: '', to_city: '', recipient_name: '', recipient_details: ''
      });
    } catch (error) {
      alert('Error creating transaction: ' + error.response?.data?.detail);
    }
  };

  const findMatches = async (transactionId) => {
    try {
      const response = await axios.get(`${API}/transactions/${transactionId}/matches`);
      setMatches(response.data);
      setSelectedTransaction(transactionId);
    } catch (error) {
      console.error('Error finding matches:', error);
    }
  };

  const createMatch = async (transactionId, matchId) => {
    if (!currentUser) {
      alert('Please register first');
      return;
    }
    
    try {
      await axios.post(`${API}/transactions/${transactionId}/match/${matchId}?user_id=${currentUser.id}`);
      alert('Match created! You can now chat with your counterparty.');
      loadTransactions();
    } catch (error) {
      alert('Error creating match: ' + error.response?.data?.detail);
    }
  };

  const loadChat = async (transactionId) => {
    try {
      const response = await axios.get(`${API}/chat/${transactionId}`);
      setChatMessages(response.data);
    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  const sendMessage = async (transactionId, receiverId) => {
    if (!currentUser || !chatInput.trim()) return;
    
    try {
      await axios.post(`${API}/chat?sender_id=${currentUser.id}`, {
        transaction_id: transactionId,
        receiver_id: receiverId,
        message: chatInput
      });
      setChatInput('');
      loadChat(transactionId);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900">
      {/* Header */}
      <nav className="bg-black/20 backdrop-blur-sm border-b border-blue-400/20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold text-white">ShaoMaCao.com</h1>
          <div className="space-x-4">
            <button 
              onClick={() => setPage('register')} 
              className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg text-white font-semibold transition-colors"
            >
              Register
            </button>
            <button 
              onClick={() => setPage('dashboard')} 
              className="border border-blue-400 hover:bg-blue-400/10 px-6 py-2 rounded-lg text-blue-100 font-semibold transition-colors"
            >
              Browse Transactions
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="bg-yellow-400/90 text-black px-4 py-2 rounded-full text-sm font-semibold inline-block">
                ⚠️ SERVICE FOR OFFSETTING FUNDS ON TRUST
              </div>
              
              <h1 className="text-5xl lg:text-7xl font-bold text-white leading-tight">
                Global Money Transfer
                <span className="text-blue-400 block">Without Borders</span>
              </h1>
              
              <p className="text-xl text-blue-100 leading-relaxed max-w-2xl">
                Connect with trusted counterparties worldwide to offset money transfers. 
                Send funds locally while your counterparty does the same - eliminating 
                international transfer fees through solidarity and trust.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => setPage('register')} 
                  className="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-lg text-white font-bold text-lg transition-colors shadow-lg"
                >
                  Start Offsetting Now
                </button>
                <button 
                  onClick={() => setPage('dashboard')} 
                  className="border-2 border-blue-400 hover:bg-blue-400/10 px-8 py-4 rounded-lg text-blue-100 font-bold text-lg transition-colors"
                >
                  Browse Available Transfers
                </button>
              </div>
            </div>
            
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1705646742193-d0ffd590193b" 
                alt="Global Network" 
                className="rounded-2xl shadow-2xl w-full h-96 object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/30 to-transparent rounded-2xl"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 px-6 bg-white/5 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-white mb-12">How It Works</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center">
                <span className="text-3xl">🌍</span>
              </div>
              <h3 className="text-2xl font-bold text-white">Find Counterparty</h3>
              <p className="text-blue-100">
                Post your transfer needs and find someone in your destination city 
                who needs to send money to your city.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center">
                <span className="text-3xl">💬</span>
              </div>
              <h3 className="text-2xl font-bold text-white">Coordinate & Chat</h3>
              <p className="text-blue-100">
                Use our secure chat system to coordinate the transaction details 
                and build trust with your counterparty.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-blue-600 rounded-full mx-auto flex items-center justify-center">
                <span className="text-3xl">✅</span>
              </div>
              <h3 className="text-2xl font-bold text-white">Admin Approval</h3>
              <p className="text-blue-100">
                Our moderator reviews and approves all offsetting agreements 
                to ensure fairness and security for all parties.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Trust Section */}
      <div className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <img 
              src="https://images.unsplash.com/photo-1655993810480-c15dccf9b3a0" 
              alt="Trust Network" 
              className="rounded-2xl shadow-2xl w-full h-96 object-cover"
            />
            
            <div className="space-y-6">
              <h2 className="text-4xl font-bold text-white">Built on Trust & Solidarity</h2>
              <p className="text-xl text-blue-100">
                Our platform operates on the principle of mutual trust and solidarity. 
                Every user is verified through ID and phone verification, and our 
                community ratings system ensures reliability.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                  <span className="text-blue-100">ID & Phone Verification Required</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                  <span className="text-blue-100">Community Rating System</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                  <span className="text-blue-100">Moderator Approval Process</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                  <span className="text-blue-100">Secure Private Messaging</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const RegisterPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900 py-12 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-blue-400/20">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Join ShaoMaCao</h1>
            <p className="text-blue-100">Register to start offsetting transactions worldwide</p>
          </div>
          
          <form onSubmit={createUser} className="space-y-6">
            <div>
              <label className="block text-blue-100 font-semibold mb-2">Username</label>
              <input
                type="text"
                value={userForm.username}
                onChange={(e) => setUserForm({...userForm, username: e.target.value})}
                className="w-full p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                placeholder="Enter your username"
                required
              />
            </div>
            
            <div>
              <label className="block text-blue-100 font-semibold mb-2">Email</label>
              <input
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                className="w-full p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                placeholder="Enter your email"
                required
              />
            </div>
            
            <div>
              <label className="block text-blue-100 font-semibold mb-2">Phone Number</label>
              <input
                type="tel"
                value={userForm.phone}
                onChange={(e) => setUserForm({...userForm, phone: e.target.value})}
                className="w-full p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                placeholder="Enter your phone number"
                required
              />
            </div>
            
            <div>
              <label className="block text-blue-100 font-semibold mb-2">ID Document Number</label>
              <input
                type="text"
                value={userForm.id_document}
                onChange={(e) => setUserForm({...userForm, id_document: e.target.value})}
                className="w-full p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                placeholder="Passport or National ID number"
                required
              />
            </div>
            
            <div>
              <label className="block text-blue-100 font-semibold mb-2">City</label>
              <select
                value={userForm.city}
                onChange={(e) => setUserForm({...userForm, city: e.target.value})}
                className="w-full p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white"
                required
              >
                <option value="">Select your city</option>
                {cities.map(city => (
                  <option key={city} value={city} className="text-black">{city}</option>
                ))}
              </select>
            </div>
            
            <button 
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Register Account
            </button>
          </form>
          
          <div className="text-center mt-6">
            <button 
              onClick={() => setPage('home')} 
              className="text-blue-400 hover:text-blue-300 underline"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const DashboardPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900">
      <nav className="bg-black/20 backdrop-blur-sm border-b border-blue-400/20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">ShaoMaCao Dashboard</h1>
          <div className="flex items-center space-x-4">
            {currentUser && (
              <span className="text-blue-100">Welcome, {currentUser.username}!</span>
            )}
            <button 
              onClick={() => setPage('home')} 
              className="text-blue-400 hover:text-blue-300 underline"
            >
              Home
            </button>
            {!currentUser && (
              <button 
                onClick={() => setPage('register')} 
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white font-semibold"
              >
                Register
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="p-6 max-w-7xl mx-auto">
        {/* Post Transaction Form */}
        {currentUser && (
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 mb-8 border border-blue-400/20">
            <h2 className="text-2xl font-bold text-white mb-4">Post New Transaction</h2>
            <form onSubmit={createTransaction} className="grid md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Transaction Title"
                value={transactionForm.title}
                onChange={(e) => setTransactionForm({...transactionForm, title: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                required
              />
              <input
                type="number"
                placeholder="Amount"
                value={transactionForm.amount}
                onChange={(e) => setTransactionForm({...transactionForm, amount: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                required
              />
              <select
                value={transactionForm.currency}
                onChange={(e) => setTransactionForm({...transactionForm, currency: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white"
              >
                <option value="USD" className="text-black">USD</option>
                <option value="EUR" className="text-black">EUR</option>
                <option value="GBP" className="text-black">GBP</option>
                <option value="JPY" className="text-black">JPY</option>
              </select>
              <select
                value={transactionForm.from_city}
                onChange={(e) => setTransactionForm({...transactionForm, from_city: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white"
                required
              >
                <option value="">From City</option>
                {cities.map(city => (
                  <option key={city} value={city} className="text-black">{city}</option>
                ))}
              </select>
              <select
                value={transactionForm.to_city}
                onChange={(e) => setTransactionForm({...transactionForm, to_city: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white"
                required
              >
                <option value="">To City</option>
                {cities.map(city => (
                  <option key={city} value={city} className="text-black">{city}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Recipient Name"
                value={transactionForm.recipient_name}
                onChange={(e) => setTransactionForm({...transactionForm, recipient_name: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200"
                required
              />
              <textarea
                placeholder="Description and recipient details"
                value={transactionForm.description}
                onChange={(e) => setTransactionForm({...transactionForm, description: e.target.value})}
                className="p-3 rounded-lg bg-white/10 border border-blue-400/30 text-white placeholder-blue-200 md:col-span-2"
                rows="3"
                required
              />
              <button 
                type="submit"
                className="md:col-span-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                Post Transaction
              </button>
            </form>
          </div>
        )}

        {/* Active Transactions */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-blue-400/20">
          <h2 className="text-2xl font-bold text-white mb-6">Available Transactions</h2>
          <div className="space-y-4">
            {transactions.map(transaction => (
              <div key={transaction.id} className="bg-white/5 rounded-lg p-4 border border-blue-400/10">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-white text-lg">{transaction.title}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    transaction.status === 'active' ? 'bg-green-500/20 text-green-200' :
                    transaction.status === 'matched' ? 'bg-yellow-500/20 text-yellow-200' :
                    'bg-gray-500/20 text-gray-200'
                  }`}>
                    {transaction.status}
                  </span>
                </div>
                <p className="text-blue-100 mb-3">{transaction.description}</p>
                <div className="grid md:grid-cols-4 gap-4 text-sm text-blue-200 mb-4">
                  <div>
                    <span className="font-semibold">Amount:</span> {transaction.currency} {transaction.amount}
                  </div>
                  <div>
                    <span className="font-semibold">From:</span> {transaction.from_city}
                  </div>
                  <div>
                    <span className="font-semibold">To:</span> {transaction.to_city}
                  </div>
                  <div>
                    <span className="font-semibold">Recipient:</span> {transaction.recipient_name}
                  </div>
                </div>
                <div className="flex space-x-3">
                  {transaction.status === 'active' && (
                    <button
                      onClick={() => findMatches(transaction.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                    >
                      Find Matches
                    </button>
                  )}
                  {(transaction.status === 'matched' || transaction.status === 'pending_approval') && (
                    <button
                      onClick={() => loadChat(transaction.id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                    >
                      Open Chat
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Matches Modal */}
        {matches.length > 0 && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Potential Matches</h3>
              <div className="space-y-4 mb-6">
                {matches.map(match => (
                  <div key={match.id} className="bg-gray-100 rounded-lg p-4 border">
                    <h4 className="font-bold text-gray-800">{match.title}</h4>
                    <p className="text-gray-600 mb-2">{match.description}</p>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-700 mb-3">
                      <div><span className="font-semibold">Amount:</span> {match.currency} {match.amount}</div>
                      <div><span className="font-semibold">From:</span> {match.from_city}</div>
                      <div><span className="font-semibold">To:</span> {match.to_city}</div>
                      <div><span className="font-semibold">Recipient:</span> {match.recipient_name}</div>
                    </div>
                    <button
                      onClick={() => createMatch(selectedTransaction, match.id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                    >
                      Create Match
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setMatches([])}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Chat Modal */}
        {chatMessages.length > 0 && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6 z-50">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] flex flex-col">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">Transaction Chat</h3>
              <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                {chatMessages.map(message => (
                  <div key={message.id} className={`flex ${message.sender_id === currentUser?.id ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.sender_id === currentUser?.id 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-800'
                    }`}>
                      <p>{message.message}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 p-3 rounded-lg border border-gray-300 text-gray-800"
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage(selectedTransaction, 'receiver-id')}
                />
                <button
                  onClick={() => sendMessage(selectedTransaction, 'receiver-id')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                >
                  Send
                </button>
              </div>
              <button
                onClick={() => setChatMessages([])}
                className="mt-4 bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Close Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Page routing
  if (page === 'register') return <RegisterPage />;
  if (page === 'dashboard') return <DashboardPage />;
  return <HomePage />;
}

export default App;