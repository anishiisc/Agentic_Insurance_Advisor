/**
 * Insurance Policy Advisor - Main Application Component (Enhanced)
 * =================================================================
 * This is the main React component that orchestrates the chat interface.
 * 
 * Features:
 * - Multi-turn conversation with session management
 * - Real-time message streaming feel
 * - Error handling and loading states
 * - Responsive design
 * - Chat termination handling with prominent Reset button
 * - Follow-up prompts after insurance details provided
 * - Graceful exit handling (bye, done, no thanks, etc.)
 */
import { useState, useRef, useEffect, useCallback } from 'react'
import ChatWindow from './components/ChatWindow'
import InputBox from './components/InputBox'
import Header from './components/Header'

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Initial welcome message
const WELCOME_MESSAGE = {
  role: 'assistant',
  content: `Namaste! 🙏 I'm **Bima Buddy**, your Insurance Advisor.

I can help you find the right insurance policy for your needs. I specialize in:

• **Health Insurance** - Individual, Family Floater, Senior Citizen plans
• **Term Life Insurance** - Pure protection plans  
• **Motor Insurance** - Car and Two-wheeler coverage
• **Travel Insurance** - Domestic and International trips

What type of insurance are you looking for today?`,
  timestamp: new Date().toISOString()
}

function App() {
  // State management
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [error, setError] = useState(null)
  const [chatEnded, setChatEnded] = useState(false)
  const [endReason, setEndReason] = useState('')
  
  // Ref for auto-scrolling
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /**
   * Send a message to the backend and handle the response
   */
  const sendMessage = useCallback(async (userMessage) => {
    if (!userMessage.trim() || isLoading || chatEnded) return

    // Clear any previous errors
    setError(null)

    // Add user message to chat immediately
    const userMsg = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Store session ID for conversation continuity
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }

      // Check if chat was ended
      if (data.chat_ended) {
        setChatEnded(true)
        setEndReason(data.end_reason || 'conversation_complete')
      }

      // Add assistant response
      const assistantMsg = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        guardrailTriggered: data.guardrail_triggered,
        chatEnded: data.chat_ended
      }
      setMessages(prev => [...prev, assistantMsg])

    } catch (err) {
      console.error('Chat error:', err)
      
      // Add error message
      const errorMsg = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again or click Reset Chat to start over.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMsg])
      setError('Failed to send message. Please check your connection.')
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, isLoading, chatEnded])

  /**
   * Clear the chat and start a new conversation (Reset)
   */
  const clearChat = useCallback(async () => {
    // Clear session on backend if exists
    if (sessionId) {
      try {
        await fetch(`${API_URL}/session/${sessionId}`, {
          method: 'DELETE'
        })
      } catch (err) {
        console.error('Failed to clear session:', err)
      }
    }

    // Reset all local state
    setMessages([{
      ...WELCOME_MESSAGE,
      content: `Chat reset! 🔄 Let's start fresh.

${WELCOME_MESSAGE.content.split('\n\n').slice(1).join('\n\n')}`,
      timestamp: new Date().toISOString()
    }])
    setSessionId(null)
    setError(null)
    setChatEnded(false)
    setEndReason('')
  }, [sessionId])

  /**
   * Quick action buttons for common queries
   */
  const handleQuickAction = useCallback((action) => {
    if (chatEnded) return // Don't allow quick actions if chat ended
    
    const quickMessages = {
      health: "I'm looking for health insurance for my family",
      term: "I need term life insurance",
      motor: "I want to buy car insurance",
      travel: "I need travel insurance for an international trip"
    }
    sendMessage(quickMessages[action])
  }, [sendMessage, chatEnded])

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <Header onClearChat={clearChat} sessionId={sessionId} />

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full overflow-hidden">
        {/* Chat Window */}
        <div className="flex-1 overflow-hidden p-4">
          <ChatWindow 
            messages={messages} 
            isLoading={isLoading}
            onQuickAction={handleQuickAction}
            showQuickActions={messages.length === 1 && !chatEnded}
          />
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Ended Banner with Reset Button */}
        {chatEnded && (
          <div className="px-4 py-4 mx-4 mb-2 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-800 font-medium">
                  {endReason === 'user_requested_exit' || endReason === 'user_declined_continue'
                    ? '✅ Conversation completed'
                    : '💬 Chat session ended'}
                </p>
                <p className="text-blue-600 text-sm mt-1">
                  Click Reset Chat to start a new conversation
                </p>
              </div>
              <button 
                onClick={clearChat}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg 
                         shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
              >
                🔄 Reset Chat
              </button>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="px-4 py-2 mx-4 mb-2 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
            {error}
            <button 
              onClick={() => setError(null)}
              className="ml-2 text-red-800 hover:text-red-900 font-medium"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 bg-white border-t">
          {chatEnded ? (
            // Show centered Reset button when chat is ended
            <div className="flex flex-col items-center justify-center py-4">
              <p className="text-gray-500 mb-4">This conversation has ended.</p>
              <button 
                onClick={clearChat}
                className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg 
                         shadow-md hover:shadow-lg transition-all duration-200 flex items-center gap-2"
              >
                <span>🔄</span>
                <span>Start New Conversation</span>
              </button>
            </div>
          ) : (
            <>
              <InputBox 
                onSend={sendMessage} 
                disabled={isLoading}
                placeholder={isLoading ? "Please wait..." : "Ask about insurance policies..."}
              />
              <p className="text-xs text-gray-500 mt-2 text-center">
                Bima Buddy is an AI assistant for educational purposes. 
                Please consult a licensed advisor for actual insurance decisions.
                <br />
                <span className="text-gray-400">
                  Type "bye" or "done" to end the conversation.
                </span>
              </p>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
