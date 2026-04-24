-- TripForge Enterprise Database Schema
-- Multi-tenant travel agency SaaS with AI agent

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- AGENCIES (Tenants)
-- ============================================
CREATE TABLE agencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    branding_config JSONB DEFAULT '{
        "primaryColor": "#E85D04",
        "logoUrl": null,
        "emailTemplate": "default"
    }'::jsonb,
    settings JSONB DEFAULT '{
        "defaultMarkupPercent": 10,
        "currency": "EUR",
        "timezone": "Europe/Berlin"
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE agencies IS 'Travel agency tenants - each agency is completely isolated';

-- ============================================
-- USERS (Agency Staff)
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'agent')),
    auth_user_id UUID REFERENCES auth.users(id), -- Supabase Auth linkage
    preferences JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agency_id, email)
);

COMMENT ON TABLE users IS 'Agency staff members with role-based access';

-- ============================================
-- CLIENTS (Travelers)
-- ============================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    preferences JSONB DEFAULT '{
        "budgetRange": null,
        "travelStyle": null,
        "dietaryRestrictions": [],
        "accessibilityNeeds": null
    }'::jsonb,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agency_id, email)
);

COMMENT ON TABLE clients IS 'Travel agency clients/customers';

-- ============================================
-- CONVERSATIONS (AI Agent Sessions)
-- ============================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id), -- Staff member managing
    title TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'pending_approval', 'closed', 'archived')),
    destination TEXT, -- Extracted from conversation
    travel_dates JSONB, -- {start_date, end_date, flexible: boolean}
    summary TEXT, -- AI-generated summary when closed
    metadata JSONB DEFAULT '{}'::jsonb, -- Additional conversation data
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE conversations IS 'AI agent conversation sessions between staff and Claude';

-- ============================================
-- MESSAGES (Conversation History)
-- ============================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'tool', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB, -- For assistant messages with tool_use
    tool_results JSONB, -- For tool role messages
    model TEXT, -- Claude model used (for assistant messages)
    tokens_used INTEGER, -- Token count for this message
    latency_ms INTEGER, -- Response time
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE messages IS 'Individual messages within AI conversations';

-- ============================================
-- OFFERS (Generated Travel Offers)
-- ============================================
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    destination TEXT NOT NULL,
    description TEXT,
    content_json JSONB NOT NULL DEFAULT '{}'::jsonb, -- Full structured offer data

    -- Pricing breakdown
    pricing JSONB DEFAULT '{
        "baseCost": 0,
        "markup": 0,
        "fees": 0,
        "total": 0,
        "currency": "EUR"
    }'::jsonb,

    -- Itinerary and flights stored separately for quick access
    itinerary JSONB, -- Array of day-by-day details
    flights JSONB, -- Array of flight segments

    -- PDF generation
    pdf_url TEXT,
    pdf_generated_at TIMESTAMPTZ,

    -- Workflow status
    status TEXT NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'sent', 'converted', 'expired')),

    -- Approval workflow
    submitted_for_approval_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Client delivery
    sent_at TIMESTAMPTZ,
    sent_method TEXT CHECK (sent_method IN ('email', 'link', 'manual')),

    -- Expiration
    valid_until DATE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE offers IS 'AI-generated travel offers with full approval workflow';

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE agencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's agency_id
CREATE OR REPLACE FUNCTION get_current_agency_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_agency_id', TRUE)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Agencies: Users can only see their own agency
CREATE POLICY agency_isolation ON agencies
    FOR ALL
    USING (id = get_current_agency_id());

-- Users: Only users in the same agency
CREATE POLICY user_agency_isolation ON users
    FOR ALL
    USING (agency_id = get_current_agency_id());

-- Clients: Only clients in the same agency
CREATE POLICY client_agency_isolation ON clients
    FOR ALL
    USING (agency_id = get_current_agency_id());

-- Conversations: Only conversations in the same agency
CREATE POLICY conversation_agency_isolation ON conversations
    FOR ALL
    USING (agency_id = get_current_agency_id());

-- Messages: Access through conversation membership
CREATE POLICY message_conversation_isolation ON messages
    FOR ALL
    USING (
        conversation_id IN (
            SELECT id FROM conversations
            WHERE agency_id = get_current_agency_id()
        )
    );

-- Offers: Only offers in the same agency
CREATE POLICY offer_agency_isolation ON offers
    FOR ALL
    USING (agency_id = get_current_agency_id());

-- ============================================
-- INDEXES
-- ============================================

-- Agency lookups
CREATE INDEX idx_users_agency_id ON users(agency_id);
CREATE INDEX idx_clients_agency_id ON clients(agency_id);
CREATE INDEX idx_conversations_agency_id ON conversations(agency_id);
CREATE INDEX idx_offers_agency_id ON offers(agency_id);

-- Conversation relationships
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_conversations_client_id ON conversations(client_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);

-- Offer lookups
CREATE INDEX idx_offers_conversation_id ON offers(conversation_id);
CREATE INDEX idx_offers_client_id ON offers(client_id);
CREATE INDEX idx_offers_status ON offers(status);
CREATE INDEX idx_offers_created_by ON offers(created_by);

-- Search indexes
CREATE INDEX idx_clients_email ON clients(email);
CREATE INDEX idx_offers_destination ON offers(destination);

-- ============================================
-- TRIGGERS (Auto-update updated_at)
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agencies_updated_at BEFORE UPDATE ON agencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_offers_updated_at BEFORE UPDATE ON offers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- REALTIME SUBSCRIPTIONS
-- ============================================

-- Enable realtime for conversations and offers
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
ALTER PUBLICATION supabase_realtime ADD TABLE offers;
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
