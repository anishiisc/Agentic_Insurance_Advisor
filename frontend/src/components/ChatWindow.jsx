/**
 * ChatWindow Component
 * ====================
 * Displays the conversation messages with proper styling
 */
import PropTypes from 'prop-types'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import QuickActions from './QuickActions'

function ChatWindow({ messages, isLoading, onQuickAction, showQuickActions }) {
  return (
    <div className="h-full bg-white rounded-xl shadow-sm overflow-hidden flex flex-col">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((message, index) => (
          <MessageBubble 
            key={index} 
            message={message}
            isLatest={index === messages.length - 1}
          />
        ))}
        
        {/* Loading indicator */}
        {isLoading && <TypingIndicator />}
      </div>

      {/* Quick action buttons */}
      {showQuickActions && !isLoading && (
        <div className="p-4 border-t bg-gray-50">
          <QuickActions onAction={onQuickAction} />
        </div>
      )}
    </div>
  )
}

ChatWindow.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      role: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      timestamp: PropTypes.string,
      isError: PropTypes.bool,
      guardrailTriggered: PropTypes.bool
    })
  ).isRequired,
  isLoading: PropTypes.bool,
  onQuickAction: PropTypes.func,
  showQuickActions: PropTypes.bool
}

ChatWindow.defaultProps = {
  isLoading: false,
  showQuickActions: false
}

export default ChatWindow
