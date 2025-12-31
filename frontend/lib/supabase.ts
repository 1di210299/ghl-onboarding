/**
 * Supabase client configuration
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * Database types
 */

export interface Client {
  id: string
  tenant_id: string
  practice_name: string
  legal_name: string | null
  address: {
    street: string
    city: string
    state: string
    zip: string
  } | null
  website: string | null
  email: string | null
  phone: string | null
  social_links: {
    facebook?: string
    instagram?: string
    linkedin?: string
    twitter?: string
  } | null
  terminology_preference: 'patients' | 'members' | 'clients' | null
  brand_colors: {
    primary: string
    secondary: string
  } | null
  business_goals: string[] | null
  ghl_contact_id: string | null
  onboarding_completed: boolean
  onboarding_data: any
  created_at: string
  updated_at: string
}

export interface Tenant {
  id: string
  name: string
  created_at: string
  updated_at: string
}
