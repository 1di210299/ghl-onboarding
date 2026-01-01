'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { type Client } from '@/lib/supabase'
import { ClientCard } from '@/components/client-card'
import { ConversationHistory } from '@/components/conversation-history'
import { Button } from '@/components/ui/button'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import { formatDate } from '@/lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function ClientDetailPage() {
  const params = useParams()
  const clientId = params.id as string

  const { data: client, isLoading } = useQuery({
    queryKey: ['client', clientId],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/clients/${clientId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch client')
      }
      const data = await response.json()
      return data as Client
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  if (!client) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Client not found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4">
        <div className="mb-6">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {client.practice_name}
          </h1>
          <p className="text-gray-600">
            Created {formatDate(client.created_at)}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <ClientCard client={client} />

            {client.onboarding_data?.messages && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">
                  Onboarding Conversation
                </h2>
                <ConversationHistory
                  messages={client.onboarding_data.messages}
                  clientName={client.practice_name}
                />
              </div>
            )}
          </div>

          <div className="space-y-6">
            {client.ghl_contact_id && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">GoHighLevel</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Contact ID</p>
                    <p className="font-mono text-sm">{client.ghl_contact_id}</p>
                  </div>
                  <Link
                    href={`https://app.thepracticesuite.com/v2/location/${process.env.NEXT_PUBLIC_GHL_LOCATION_ID}/contacts/detail/${client.ghl_contact_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Button variant="outline" size="sm" className="w-full">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View in GHL
                    </Button>
                  </Link>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Status</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Onboarding</p>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      client.onboarding_completed
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {client.onboarding_completed ? 'Completed' : 'Pending'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
