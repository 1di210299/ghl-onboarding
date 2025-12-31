'use client'

import { formatDateTime } from '@/lib/utils'

interface Message {
  role: 'assistant' | 'user'
  content: string
  timestamp?: string
}

interface ConversationHistoryProps {
  messages: Message[]
}

export function ConversationHistory({ messages }: ConversationHistoryProps) {
  if (!messages || messages.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No conversation history available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-[80%] rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-900'
            }`}
          >
            <div className="flex items-start gap-2 mb-1">
              <span className="text-xs font-medium opacity-75">
                {message.role === 'user' ? 'Client' : 'Assistant'}
              </span>
              {message.timestamp && (
                <span className="text-xs opacity-50">
                  {formatDateTime(message.timestamp)}
                </span>
              )}
            </div>
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
