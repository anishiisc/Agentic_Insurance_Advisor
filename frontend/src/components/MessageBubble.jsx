/**
 * MessageBubble Component
 * =======================
 * Renders individual chat messages with appropriate styling
 */
import PropTypes from 'prop-types'

function MessageBubble({ message, isLatest }) {
  const isUser = message.role === 'user'
  const isError = message.isError
  const guardrailTriggered = message.guardrailTriggered

  // Format timestamp
  const formattedTime = message.timestamp 
    ? new Date(message.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    : ''

  /**
   * Simple markdown-like formatting for the message content
   * Handles: **bold**, bullet points, numbered lists
   */
  const formatContent = (content) => {
    // Split into paragraphs
    const paragraphs = content.split('\n\n')
    
    return paragraphs.map((paragraph, pIdx) => {
      // Check if it's a bullet list
      if (paragraph.includes('• ') || paragraph.match(/^- /m)) {
        const items = paragraph.split('\n').filter(line => line.trim())
        return (
          <ul key={pIdx} className="list-none space-y-1 my-2">
            {items.map((item, iIdx) => {
              const cleanItem = item.replace(/^[•\-]\s*/, '')
              return (
                <li key={iIdx} className="flex gap-2">
                  <span className="text-primary-500">•</span>
                  <span dangerouslySetInnerHTML={{ 
                    __html: cleanItem.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                  }} />
                </li>
              )
            })}
          </ul>
        )
      }

      // Regular paragraph with bold formatting
      return (
        <p 
          key={pIdx} 
          className="my-2"
          dangerouslySetInnerHTML={{ 
            __html: paragraph
              .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
              .replace(/\n/g, '<br />')
          }} 
        />
      )
    })
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
          ${isUser 
            ? 'bg-primary-100 text-primary-600' 
            : isError 
              ? 'bg-red-100 text-red-600'
              : 'bg-gradient-to-br from-primary-500 to-primary-600 text-white'
          }`}
        >
          {isUser ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          ) : (
            <span className="text-sm">🛡️</span>
          )}
        </div>

        {/* Message content */}
        <div className="flex flex-col">
          <div 
            className={`rounded-2xl px-4 py-3 ${
              isUser 
                ? 'bg-primary-600 text-white rounded-br-md' 
                : isError
                  ? 'bg-red-50 text-red-800 border border-red-200 rounded-bl-md'
                  : guardrailTriggered
                    ? 'bg-amber-50 text-gray-800 border border-amber-200 rounded-bl-md'
                    : 'bg-gray-100 text-gray-800 rounded-bl-md'
            }`}
          >
            {/* Role label for assistant */}
            {!isUser && (
              <div className={`text-xs font-medium mb-1 ${
                isError ? 'text-red-600' : 'text-primary-600'
              }`}>
                Bima Buddy
              </div>
            )}
            
            {/* Message content */}
            <div className="message-content text-sm leading-relaxed">
              {formatContent(message.content)}
            </div>

            {/* Guardrail indicator */}
            {guardrailTriggered && (
              <div className="mt-2 pt-2 border-t border-amber-200 text-xs text-amber-600 flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Safety disclaimer added
              </div>
            )}
          </div>

          {/* Timestamp */}
          {formattedTime && (
            <span className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
              {formattedTime}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

MessageBubble.propTypes = {
  message: PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.string,
    isError: PropTypes.bool,
    guardrailTriggered: PropTypes.bool
  }).isRequired,
  isLatest: PropTypes.bool
}

export default MessageBubble
