/**
 * TypingIndicator Component
 * =========================
 * Shows an animated typing indicator when the AI is processing
 */

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex gap-3 max-w-[85%]">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
          <span className="text-sm">🛡️</span>
        </div>

        {/* Typing bubble */}
        <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
            <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
            <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
