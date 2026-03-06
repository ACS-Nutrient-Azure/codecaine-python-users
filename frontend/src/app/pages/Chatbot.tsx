import { useState } from 'react';
import { Send, Smile, User } from 'lucide-react';

export function Chatbot() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: '홍길동님의 영양제 추천 분석 기록입니다.',
      timestamp: '2026.02.10',
    },
    {
      type: 'bot',
      content: '이 분석 결과를 바탕으로 상담을 시작합니다',
    },
  ]);

  const handleSend = () => {
    if (message.trim()) {
      setMessages([...messages, { type: 'user', content: message }]);
      setMessage('');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">영양제 추천 결과</h1>
        <div className="flex items-center gap-3">
          <User className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">홍길동님</span>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-8 bg-gray-50">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Date Header */}
          <div className="text-center">
            <span className="text-sm text-gray-500">2026.02.10</span>
          </div>

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                msg.type === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              {msg.type === 'bot' && (
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-gray-500" />
                </div>
              )}
              
              <div
                className={`max-w-md rounded-2xl px-5 py-3 ${
                  msg.type === 'bot'
                    ? 'bg-white shadow-sm border border-gray-200'
                    : 'bg-blue-500 text-white'
                }`}
              >
                <p className={msg.type === 'bot' ? 'text-gray-800' : 'text-white'}>
                  {msg.content}
                </p>
                {msg.timestamp && (
                  <p className="text-xs text-gray-400 mt-1">{msg.timestamp}</p>
                )}
              </div>

              {msg.type === 'user' && (
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Message Input */}
      <div className="border-t border-gray-200 px-6 py-4 bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3 bg-gray-100 rounded-full px-5 py-3">
            <button className="text-gray-400 hover:text-gray-600 transition-colors">
              <Smile className="w-5 h-5" />
            </button>
            
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="메시지를 입력하세요..."
              className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-400"
            />
            
            <button
              onClick={handleSend}
              className="text-blue-500 hover:text-blue-600 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
