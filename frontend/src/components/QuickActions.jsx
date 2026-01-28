/**
 * QuickActions Component
 * ======================
 * Provides quick action buttons for common insurance queries
 */
import PropTypes from 'prop-types'

function QuickActions({ onAction }) {
  const actions = [
    {
      id: 'health',
      label: 'Health Insurance',
      icon: '🏥',
      color: 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200'
    },
    {
      id: 'term',
      label: 'Term Life',
      icon: '🛡️',
      color: 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200'
    },
    {
      id: 'motor',
      label: 'Motor Insurance',
      icon: '🚗',
      color: 'bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-200'
    },
    {
      id: 'travel',
      label: 'Travel Insurance',
      icon: '✈️',
      color: 'bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-200'
    }
  ]

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500 text-center">Quick Start</p>
      <div className="flex flex-wrap gap-2 justify-center">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-medium
              ${action.color} transition-colors duration-150`}
          >
            <span>{action.icon}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

QuickActions.propTypes = {
  onAction: PropTypes.func.isRequired
}

export default QuickActions
