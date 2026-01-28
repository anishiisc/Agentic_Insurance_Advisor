/**
 * InputBox Component
 * ==================
 * Text input field with send button for chat messages
 */
import { useState, useRef, useEffect } from 'react'
import PropTypes from 'prop-types'

function InputBox({ onSend, disabled, placeholder }) {
  const [input, setInput] = useState('')
  const inputRef = useRef(null)

  // Auto-focus on mount and when re-enabled
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus()
    }
  }, [disabled])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      {/* Text Input */}
      <div className="flex-1 relative">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          maxLength={2000}
          className={`w-full px-4 py-3 border rounded-xl text-sm
            ${disabled 
              ? 'bg-gray-100 text-gray-500 cursor-not-allowed' 
              : 'bg-white hover:border-primary-300'
            }
            border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
            transition-all duration-150`}
        />
        
        {/* Character count (shown when > 1500) */}
        {input.length > 1500 && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
            {input.length}/2000
          </span>
        )}
      </div>

      {/* Send Button */}
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className={`px-5 py-3 rounded-xl font-medium flex items-center gap-2
          ${disabled || !input.trim()
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white'
          }
          transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`}
        title={disabled ? 'Please wait...' : 'Send message'}
      >
        {disabled ? (
          // Loading spinner
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          // Send icon
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
            />
          </svg>
        )}
        <span className="hidden sm:inline">
          {disabled ? 'Sending...' : 'Send'}
        </span>
      </button>
    </form>
  )
}

InputBox.propTypes = {
  onSend: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  placeholder: PropTypes.string
}

InputBox.defaultProps = {
  disabled: false,
  placeholder: 'Type your message...'
}

export default InputBox
