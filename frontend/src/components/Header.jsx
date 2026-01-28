/**
 * Header Component
 * ================
 * Application header with branding and controls
 * Enhanced with more prominent Reset Chat button
 */
import PropTypes from 'prop-types'

function Header({ onClearChat, sessionId }) {
  return (
    <header className="bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg">
      <div className="max-w-4xl mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-2xl">🛡️</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Bima Buddy</h1>
              <p className="text-xs text-primary-200">Your Insurance Advisor</p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4">
            {/* Session indicator */}
            {sessionId && (
              <span className="text-xs text-primary-200 hidden sm:block">
                Session active
              </span>
            )}
            
            {/* Reset Chat button - More prominent */}
            <button
              onClick={onClearChat}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 
                         border border-white/30 rounded-lg text-sm font-semibold 
                         transition-all duration-200 hover:scale-105 shadow-sm"
              title="Reset conversation and start fresh"
            >
              <svg 
                className="w-4 h-4" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                />
              </svg>
              <span>Reset Chat</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

Header.propTypes = {
  onClearChat: PropTypes.func.isRequired,
  sessionId: PropTypes.string
}

export default Header
