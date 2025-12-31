'use client'

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { supabase, type Client } from '@/lib/supabase'
import { ClientsTable } from '@/components/clients-table'
import { SearchBar } from '@/components/search-bar'
import { Button } from '@/components/ui/button'
import { Download, Plus } from 'lucide-react'
import { exportToCSV } from '@/lib/utils'

// Demo tenant ID - in production, get from auth
const TENANT_ID = '00000000-0000-0000-0000-000000000001'

export default function DashboardPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [terminologyFilter, setTerminologyFilter] = useState<
    string | undefined
  >()

  // Fetch clients from Backend API
  const { data: clients, isLoading, error } = useQuery({
    queryKey: ['clients', TENANT_ID, search, statusFilter, terminologyFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        tenant_id: TENANT_ID,
      })
      
      if (search) params.append('search', search)
      if (statusFilter) params.append('status', statusFilter)
      if (terminologyFilter) params.append('terminology', terminologyFilter)

      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/clients?${params}`
      console.log('Fetching clients from:', url)
      
      const response = await fetch(url)

      if (!response.ok) {
        console.error('Failed to fetch clients:', response.status, response.statusText)
        throw new Error('Failed to fetch clients')
      }
      
      const data = await response.json()
      console.log('Received data:', data)
      console.log('Clients count:', data.clients?.length)
      return data.clients as Client[]
    },
  })

  // Log any errors
  if (error) {
    console.error('Query error:', error)
  }

  const handleExport = () => {
    if (!clients) return

    const exportData = clients.map((client) => ({
      practice_name: client.practice_name,
      email: client.email || '',
      phone: client.phone || '',
      status: client.onboarding_completed ? 'Completed' : 'Pending',
      terminology: client.terminology_preference || '',
      created_at: client.created_at,
    }))

    exportToCSV(exportData, 'clients-export')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Client Dashboard
          </h1>
          <p className="text-gray-600">
            Manage and monitor healthcare practice onboarding
          </p>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
              <SearchBar value={search} onChange={setSearch} />

              <div className="flex gap-2">
                <select
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm"
                  value={statusFilter || ''}
                  onChange={(e) =>
                    setStatusFilter(e.target.value || undefined)
                  }
                >
                  <option value="">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="pending">Pending</option>
                </select>

                <select
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm"
                  value={terminologyFilter || ''}
                  onChange={(e) =>
                    setTerminologyFilter(e.target.value || undefined)
                  }
                >
                  <option value="">All Terminology</option>
                  <option value="patients">Patients</option>
                  <option value="members">Members</option>
                  <option value="clients">Clients</option>
                </select>

                <Button onClick={handleExport} variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            </div>
          </div>

          <ClientsTable clients={clients || []} isLoading={isLoading} />
        </div>

        <div className="mt-6 flex justify-between items-center text-sm text-gray-600">
          <p>Total clients: {clients?.length || 0}</p>
          <p>
            Completed:{' '}
            {clients?.filter((c) => c.onboarding_completed).length || 0}
          </p>
        </div>
      </div>
    </div>
  )
}
