'use client'

import { formatDateTime } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'

interface Message {
  role: 'assistant' | 'user'
  content: string
  timestamp?: string
}

interface ConversationHistoryProps {
  messages: Message[]
  clientName?: string
}

export function ConversationHistory({ messages, clientName }: ConversationHistoryProps) {
  if (!messages || messages.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No conversation history available
      </div>
    )
  }

  const handleDownloadJSON = () => {
    const conversationData = {
      client: clientName || 'Unknown',
      exportDate: new Date().toISOString(),
      totalMessages: messages.length,
      messages: messages.map((msg, idx) => ({
        messageNumber: idx + 1,
        role: msg.role,
        sender: msg.role === 'user' ? 'Client' : 'Assistant',
        content: msg.content,
        timestamp: msg.timestamp || null
      }))
    }

    const blob = new Blob([JSON.stringify(conversationData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${clientName?.replace(/\s+/g, '-').toLowerCase() || 'export'}-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-600">
          {messages.length} messages
        </p>
        <Button
          onClick={handleDownloadJSON}
          variant="outline"
          size="sm"
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          Download JSON
        </Button>
      </div>
      
      <div className="max-h-[600px] overflow-y-auto pr-2 space-y-3 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[75%] rounded-lg px-3 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold opacity-75">
                  {message.role === 'user' ? 'Client' : 'Assistant'}
                </span>
                {message.timestamp && (
                  <span className="text-xs opacity-50">
                    {formatDateTime(message.timestamp)}
                  </span>
                )}
              </div>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
