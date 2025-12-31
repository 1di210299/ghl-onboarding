-- =====================================================
-- GHL Healthcare Onboarding System - Initial Schema
-- =====================================================
-- This migration creates the complete database schema with:
-- - Multi-tenant architecture
-- - Row-Level Security (RLS)
-- - Proper indexes and constraints
-- - Automatic timestamp management
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- TABLES
-- =====================================================

-- Tenants table for multi-tenant isolation
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Clients table with all onboarding information
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Practice Information
    practice_name TEXT NOT NULL,
    legal_name TEXT,
    
    -- Contact Information
    address JSONB,  -- {street, city, state, zip}
    website TEXT,
    email TEXT,
    phone TEXT,
    
    -- Social Media
    social_links JSONB,  -- {facebook, instagram, linkedin, twitter}
    
    -- Branding
    terminology_preference TEXT CHECK (terminology_preference IN ('patients', 'members', 'clients')),
    brand_colors JSONB,  -- {primary, secondary}
    
    -- Business Information
    business_goals TEXT[],
    
    -- Integration
    ghl_contact_id TEXT,
    
    -- Onboarding Status
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_data JSONB,  -- Stores full conversation history
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_website CHECK (website IS NULL OR website ~* '^https?://'),
    CONSTRAINT unique_ghl_contact UNIQUE (ghl_contact_id)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Tenant indexes
CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(name);
CREATE INDEX IF NOT EXISTS idx_tenants_created_at ON tenants(created_at DESC);

-- Client indexes
CREATE INDEX IF NOT EXISTS idx_clients_tenant_id ON clients(tenant_id);
CREATE INDEX IF NOT EXISTS idx_clients_practice_name ON clients(practice_name);
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_clients_ghl_contact_id ON clients(ghl_contact_id);
CREATE INDEX IF NOT EXISTS idx_clients_onboarding_completed ON clients(onboarding_completed);
CREATE INDEX IF NOT EXISTS idx_clients_created_at ON clients(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clients_updated_at ON clients(updated_at DESC);

-- GIN indexes for JSONB fields (for efficient querying)
CREATE INDEX IF NOT EXISTS idx_clients_address ON clients USING GIN (address);
CREATE INDEX IF NOT EXISTS idx_clients_social_links ON clients USING GIN (social_links);
CREATE INDEX IF NOT EXISTS idx_clients_brand_colors ON clients USING GIN (brand_colors);
CREATE INDEX IF NOT EXISTS idx_clients_onboarding_data ON clients USING GIN (onboarding_data);

-- Text search index for practice name
CREATE INDEX IF NOT EXISTS idx_clients_practice_name_trgm ON clients USING GIN (practice_name gin_trgm_ops);

-- Array index for business goals
CREATE INDEX IF NOT EXISTS idx_clients_business_goals ON clients USING GIN (business_goals);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for tenants table
DROP TRIGGER IF EXISTS update_tenants_updated_at ON tenants;
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for clients table
DROP TRIGGER IF EXISTS update_clients_updated_at ON clients;
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW-LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Tenants RLS Policies
-- Users can only see their own tenant
DROP POLICY IF EXISTS tenant_isolation_policy ON tenants;
CREATE POLICY tenant_isolation_policy ON tenants
    FOR ALL
    USING (id = current_setting('app.current_tenant_id', true)::UUID);

-- Clients RLS Policies
-- Users can only see clients from their tenant
DROP POLICY IF EXISTS client_tenant_isolation_policy ON clients;
CREATE POLICY client_tenant_isolation_policy ON clients
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Service role bypass (for server-side operations)
DROP POLICY IF EXISTS service_role_all_access ON tenants;
CREATE POLICY service_role_all_access ON tenants
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS service_role_all_access_clients ON clients;
CREATE POLICY service_role_all_access_clients ON clients
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to set tenant context for RLS
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_uuid::TEXT, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get client onboarding progress
CREATE OR REPLACE FUNCTION get_onboarding_progress(client_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    client_record RECORD;
    completed_fields INTEGER := 0;
    total_fields INTEGER := 10;
    progress_percent INTEGER;
BEGIN
    SELECT * INTO client_record FROM clients WHERE id = client_uuid;
    
    IF client_record IS NULL THEN
        RETURN jsonb_build_object('error', 'Client not found');
    END IF;
    
    -- Count completed fields
    IF client_record.practice_name IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.legal_name IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.address IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.website IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.email IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.phone IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.social_links IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.terminology_preference IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.brand_colors IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    IF client_record.business_goals IS NOT NULL THEN completed_fields := completed_fields + 1; END IF;
    
    progress_percent := (completed_fields * 100) / total_fields;
    
    RETURN jsonb_build_object(
        'completed_fields', completed_fields,
        'total_fields', total_fields,
        'progress_percent', progress_percent,
        'onboarding_completed', client_record.onboarding_completed
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- SAMPLE DATA (for testing - remove in production)
-- =====================================================

-- Insert sample tenant
INSERT INTO tenants (id, name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'Demo Agency')
ON CONFLICT DO NOTHING;

-- Insert sample client
INSERT INTO clients (
    tenant_id,
    practice_name,
    legal_name,
    email,
    phone,
    terminology_preference,
    onboarding_completed
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Healthy Life Medical Center',
    'Healthy Life Medical Center LLC',
    'info@healthylifemedical.com',
    '(555) 123-4567',
    'patients',
    false
) ON CONFLICT DO NOTHING;

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON tenants TO authenticated;
GRANT SELECT, INSERT, UPDATE ON clients TO authenticated;

-- Grant usage on sequences (for auto-incrementing IDs if needed)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE tenants IS 'Stores tenant/agency information for multi-tenant isolation';
COMMENT ON TABLE clients IS 'Stores healthcare practice client information collected during onboarding';
COMMENT ON COLUMN clients.address IS 'JSON structure: {street, city, state, zip}';
COMMENT ON COLUMN clients.social_links IS 'JSON structure: {facebook, instagram, linkedin, twitter}';
COMMENT ON COLUMN clients.brand_colors IS 'JSON structure: {primary: "#hex", secondary: "#hex"}';
COMMENT ON COLUMN clients.business_goals IS 'Array of text strings representing top business goals';
COMMENT ON COLUMN clients.onboarding_data IS 'Complete conversation history and metadata from onboarding process';
COMMENT ON COLUMN clients.ghl_contact_id IS 'GoHighLevel contact ID for integration';

-- =====================================================
-- COMPLETION
-- =====================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema.sql completed successfully';
    RAISE NOTICE 'Tables created: tenants, clients';
    RAISE NOTICE 'RLS enabled on all tables';
    RAISE NOTICE 'Indexes and triggers configured';
END $$;
