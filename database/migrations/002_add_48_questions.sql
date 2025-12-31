-- =====================================================
-- Migration 002: Add 48 Questions Fields
-- =====================================================
-- Adds fields for all 48 onboarding questions
-- Organized by stage (4 JSONB columns for flexibility)
-- =====================================================

-- Add stage-based JSONB columns to clients table
ALTER TABLE clients
ADD COLUMN IF NOT EXISTS quick_start_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS team_tech_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS identity_brand_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS digital_growth_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS current_stage TEXT DEFAULT 'basics',
ADD COLUMN IF NOT EXISTS current_question INTEGER DEFAULT 0;

-- Add indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_clients_quick_start_data ON clients USING GIN (quick_start_data);
CREATE INDEX IF NOT EXISTS idx_clients_team_tech_data ON clients USING GIN (team_tech_data);
CREATE INDEX IF NOT EXISTS idx_clients_identity_brand_data ON clients USING GIN (identity_brand_data);
CREATE INDEX IF NOT EXISTS idx_clients_digital_growth_data ON clients USING GIN (digital_growth_data);

-- Add index for current_stage
CREATE INDEX IF NOT EXISTS idx_clients_current_stage ON clients(current_stage);

-- =====================================================
-- Conversation Sessions Table
-- =====================================================

CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Session state
    session_state JSONB NOT NULL DEFAULT '{}',
    current_stage TEXT NOT NULL DEFAULT 'basics',
    current_question INTEGER NOT NULL DEFAULT 0,
    
    -- Resume functionality
    resume_token TEXT UNIQUE,
    resume_token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_completed BOOLEAN DEFAULT FALSE,
    is_paused BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    last_interaction_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for conversation_sessions
CREATE INDEX IF NOT EXISTS idx_sessions_client_id ON conversation_sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_sessions_resume_token ON conversation_sessions(resume_token) WHERE resume_token IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sessions_last_interaction ON conversation_sessions(last_interaction_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_is_completed ON conversation_sessions(is_completed);
CREATE INDEX IF NOT EXISTS idx_sessions_current_stage ON conversation_sessions(current_stage);

-- GIN index for session_state JSONB
CREATE INDEX IF NOT EXISTS idx_sessions_state ON conversation_sessions USING GIN (session_state);

-- =====================================================
-- Helper Functions
-- =====================================================

-- Function to get progress by stage
CREATE OR REPLACE FUNCTION get_stage_progress(client_uuid UUID, stage_name TEXT)
RETURNS JSONB AS $$
DECLARE
    client_record RECORD;
    stage_data JSONB;
    total_fields INTEGER;
    completed_fields INTEGER;
    progress_percent INTEGER;
BEGIN
    SELECT * INTO client_record FROM clients WHERE id = client_uuid;
    
    IF client_record IS NULL THEN
        RETURN jsonb_build_object('error', 'Client not found');
    END IF;
    
    -- Get stage data based on stage name
    CASE stage_name
        WHEN 'basics' THEN
            stage_data := client_record.quick_start_data;
            total_fields := 9;
        WHEN 'team_tech' THEN
            stage_data := client_record.team_tech_data;
            total_fields := 7;
        WHEN 'identity_brand' THEN
            stage_data := client_record.identity_brand_data;
            total_fields := 12;
        WHEN 'digital_growth' THEN
            stage_data := client_record.digital_growth_data;
            total_fields := 20;
        ELSE
            RETURN jsonb_build_object('error', 'Invalid stage name');
    END CASE;
    
    -- Count non-null fields
    completed_fields := jsonb_object_keys(stage_data)::text[] FROM jsonb_object_keys(stage_data);
    
    progress_percent := CASE 
        WHEN total_fields = 0 THEN 0
        ELSE (completed_fields * 100) / total_fields
    END;
    
    RETURN jsonb_build_object(
        'stage', stage_name,
        'completed_fields', completed_fields,
        'total_fields', total_fields,
        'progress_percent', progress_percent
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update session last_interaction_at
CREATE OR REPLACE FUNCTION update_session_interaction()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_interaction_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for session updates
DROP TRIGGER IF EXISTS update_session_interaction_trigger ON conversation_sessions;
CREATE TRIGGER update_session_interaction_trigger
    BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_session_interaction();

-- =====================================================
-- RLS Policies for conversation_sessions
-- =====================================================

-- Enable RLS
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see sessions from their tenant's clients
DROP POLICY IF EXISTS session_tenant_isolation_policy ON conversation_sessions;
CREATE POLICY session_tenant_isolation_policy ON conversation_sessions
    FOR ALL
    USING (
        client_id IN (
            SELECT id FROM clients 
            WHERE tenant_id = current_setting('app.current_tenant_id', true)::UUID
        )
    );

-- Service role bypass
DROP POLICY IF EXISTS service_role_all_access_sessions ON conversation_sessions;
CREATE POLICY service_role_all_access_sessions ON conversation_sessions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- Field Mapping Documentation
-- =====================================================

COMMENT ON COLUMN clients.quick_start_data IS 'JSONB: Q1-Q9 (name, birthday, practice_name, ein, addresses, phone, email)';
COMMENT ON COLUMN clients.team_tech_data IS 'JSONB: Q10-Q16 (team, point_person, communication, tech_savvy, marketing_company, software)';
COMMENT ON COLUMN clients.identity_brand_data IS 'JSONB: Q17-Q28 (practice_type, ideal_client, boundaries, messaging, brand_voice, brand_assets)';
COMMENT ON COLUMN clients.digital_growth_data IS 'JSONB: Q29-Q48 (website, social_media, suite_management, growth_strategy, priorities)';
COMMENT ON COLUMN clients.current_stage IS 'Current onboarding stage: basics, team_tech, identity_brand, digital_growth';
COMMENT ON COLUMN clients.current_question IS 'Current question number (0-47)';

COMMENT ON TABLE conversation_sessions IS 'Stores active onboarding conversation sessions with state persistence';
COMMENT ON COLUMN conversation_sessions.session_state IS 'Complete conversation state including messages and collected data';
COMMENT ON COLUMN conversation_sessions.resume_token IS 'Unique token for pause/resume functionality';

-- =====================================================
-- Grants
-- =====================================================

GRANT SELECT, INSERT, UPDATE ON conversation_sessions TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- Completion
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 002 completed successfully';
    RAISE NOTICE 'Added stage-based JSONB columns to clients table';
    RAISE NOTICE 'Created conversation_sessions table with RLS';
    RAISE NOTICE 'Added helper functions for progress tracking';
END $$;
