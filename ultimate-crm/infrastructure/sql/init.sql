-- Ultimate CRM System Database Initialization
-- This script sets up the initial database schema and default data

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types for better performance
DO $$
BEGIN
    -- Create enum types if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customer_type') THEN
        CREATE TYPE customer_type AS ENUM ('individual', 'business', 'enterprise');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customer_status') THEN
        CREATE TYPE customer_status AS ENUM ('prospect', 'active', 'inactive', 'churned', 'blacklisted');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'lead_status') THEN
        CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'unqualified', 'converted', 'lost');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'opportunity_status') THEN
        CREATE TYPE opportunity_status AS ENUM ('open', 'won', 'lost', 'abandoned');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticket_status') THEN
        CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'waiting_customer', 'waiting_vendor', 'resolved', 'closed', 'cancelled');
    END IF;
END
$$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);

CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);

CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_amount ON opportunities(amount DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_close_date ON opportunities(expected_close_date);

CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);

CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_scheduled_at ON activities(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_activities_customer_id ON activities(customer_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_customers_search ON customers USING gin(
    to_tsvector('english', coalesce(name, '') || ' ' || coalesce(email, '') || ' ' || coalesce(phone, ''))
);

CREATE INDEX IF NOT EXISTS idx_leads_search ON leads USING gin(
    to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(company, '') || ' ' || coalesce(email, ''))
);

-- Insert default system roles
INSERT INTO roles (id, name, display_name, description, permissions, is_system_role, is_active)
VALUES 
    (uuid_generate_v4(), 'super_admin', 'Super Administrator', 'Full system access', 
     '["system.manage", "users.manage", "roles.manage", "customers.manage", "leads.manage", "opportunities.manage", "campaigns.manage", "tickets.manage", "reports.view", "settings.manage"]'::jsonb, 
     true, true),
    (uuid_generate_v4(), 'admin', 'Administrator', 'Administrative access',
     '["users.view", "users.create", "users.update", "customers.manage", "leads.manage", "opportunities.manage", "campaigns.manage", "tickets.manage", "reports.view"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'sales_manager', 'Sales Manager', 'Sales team management',
     '["leads.manage", "opportunities.manage", "customers.manage", "activities.manage", "reports.sales.view", "users.sales.view"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'sales_rep', 'Sales Representative', 'Sales activities',
     '["leads.view", "leads.update", "opportunities.view", "opportunities.update", "customers.view", "customers.update", "activities.manage"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'marketing_manager', 'Marketing Manager', 'Marketing team management',
     '["campaigns.manage", "leads.view", "customers.view", "reports.marketing.view", "content.manage"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'support_manager', 'Support Manager', 'Customer support management',
     '["tickets.manage", "customers.view", "knowledge.manage", "reports.support.view"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'support_agent', 'Support Agent', 'Customer support',
     '["tickets.view", "tickets.update", "customers.view", "knowledge.view"]'::jsonb,
     true, true),
    (uuid_generate_v4(), 'viewer', 'Viewer', 'Read-only access',
     '["customers.view", "leads.view", "opportunities.view", "tickets.view", "reports.basic.view"]'::jsonb,
     true, true)
ON CONFLICT (name) DO NOTHING;

-- Insert default opportunity stages
INSERT INTO opportunity_stages (id, name, description, order_index, probability_default, is_closed_won, is_closed_lost, color, is_active)
VALUES 
    (uuid_generate_v4(), 'Prospecting', 'Initial contact and qualification', 1, 10, false, false, '#FF6B6B', true),
    (uuid_generate_v4(), 'Qualification', 'Needs assessment and budget confirmation', 2, 25, false, false, '#4ECDC4', true),
    (uuid_generate_v4(), 'Proposal', 'Solution presentation and proposal', 3, 50, false, false, '#45B7D1', true),
    (uuid_generate_v4(), 'Negotiation', 'Contract negotiation and terms discussion', 4, 75, false, false, '#FFA726', true),
    (uuid_generate_v4(), 'Closed Won', 'Deal successfully closed', 5, 100, true, false, '#66BB6A', true),
    (uuid_generate_v4(), 'Closed Lost', 'Deal lost to competitor or abandoned', 6, 0, false, true, '#EF5350', true)
ON CONFLICT (name) DO NOTHING;

-- Insert default lead sources
INSERT INTO lead_sources (id, name, description, category, is_active)
VALUES 
    (uuid_generate_v4(), 'Website', 'Direct website inquiries', 'organic', true),
    (uuid_generate_v4(), 'Google Ads', 'Google advertising campaigns', 'paid', true),
    (uuid_generate_v4(), 'Social Media', 'Social media platforms', 'social', true),
    (uuid_generate_v4(), 'Email Campaign', 'Email marketing campaigns', 'email', true),
    (uuid_generate_v4(), 'Referral', 'Customer referrals', 'referral', true),
    (uuid_generate_v4(), 'Trade Show', 'Industry events and trade shows', 'event', true),
    (uuid_generate_v4(), 'Cold Calling', 'Outbound sales calls', 'outbound', true),
    (uuid_generate_v4(), 'Partner', 'Partner referrals', 'referral', true)
ON CONFLICT (name) DO NOTHING;

-- Insert default customer segments
INSERT INTO customer_segments (id, name, description, color, is_active, is_dynamic)
VALUES 
    (uuid_generate_v4(), 'High Value', 'Customers with high lifetime value', '#2E7D32', true, false),
    (uuid_generate_v4(), 'New Customers', 'Recently acquired customers', '#1976D2', true, false),
    (uuid_generate_v4(), 'At Risk', 'Customers at risk of churning', '#D32F2F', true, false),
    (uuid_generate_v4(), 'Enterprise', 'Large enterprise customers', '#7B1FA2', true, false),
    (uuid_generate_v4(), 'SMB', 'Small and medium business customers', '#F57C00', true, false)
ON CONFLICT (name) DO NOTHING;

-- Insert default product categories
INSERT INTO product_categories (id, name, description, slug, level, is_active, sort_order)
VALUES 
    (uuid_generate_v4(), 'Software', 'Software products and licenses', 'software', 0, true, 1),
    (uuid_generate_v4(), 'Services', 'Professional services', 'services', 0, true, 2),
    (uuid_generate_v4(), 'Support', 'Support and maintenance', 'support', 0, true, 3),
    (uuid_generate_v4(), 'Training', 'Training and certification', 'training', 0, true, 4)
ON CONFLICT (slug) DO NOTHING;

-- Insert default ticket categories
INSERT INTO ticket_categories (id, name, description, sla_hours, first_response_hours, is_active, color)
VALUES 
    (uuid_generate_v4(), 'Technical Issue', 'Technical problems and bugs', 24, 4, true, '#F44336'),
    (uuid_generate_v4(), 'Feature Request', 'New feature requests', 72, 8, true, '#2196F3'),
    (uuid_generate_v4(), 'Billing', 'Billing and payment issues', 8, 2, true, '#FF9800'),
    (uuid_generate_v4(), 'General Inquiry', 'General questions and inquiries', 48, 6, true, '#4CAF50')
ON CONFLICT (name) DO NOTHING;

-- Insert default activity types
INSERT INTO activity_types (id, name, display_name, description, icon, color, default_duration_minutes, is_billable_default, is_active)
VALUES 
    (uuid_generate_v4(), 'call', 'Phone Call', 'Phone conversation with customer', 'phone', '#2196F3', 30, false, true),
    (uuid_generate_v4(), 'email', 'Email', 'Email communication', 'email', '#4CAF50', 15, false, true),
    (uuid_generate_v4(), 'meeting', 'Meeting', 'In-person or virtual meeting', 'meeting', '#FF9800', 60, true, true),
    (uuid_generate_v4(), 'demo', 'Product Demo', 'Product demonstration', 'presentation', '#9C27B0', 45, true, true),
    (uuid_generate_v4(), 'proposal', 'Proposal', 'Proposal creation and delivery', 'document', '#607D8B', 120, true, true)
ON CONFLICT (name) DO NOTHING;

-- Create a function to generate sequential numbers
CREATE OR REPLACE FUNCTION generate_sequential_number(prefix TEXT, table_name TEXT, column_name TEXT)
RETURNS TEXT AS $$
DECLARE
    next_number INTEGER;
    result TEXT;
BEGIN
    -- Get the next number in sequence
    EXECUTE format('SELECT COALESCE(MAX(CAST(SUBSTRING(%I FROM %s) AS INTEGER)), 0) + 1 FROM %I WHERE %I LIKE %L',
                   column_name, length(prefix) + 1, table_name, column_name, prefix || '%')
    INTO next_number;
    
    -- Format the result with leading zeros
    result := prefix || LPAD(next_number::TEXT, 6, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for auto-generating numbers
CREATE OR REPLACE FUNCTION generate_customer_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.customer_number IS NULL THEN
        NEW.customer_number := generate_sequential_number('CUST-', 'customers', 'customer_number');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_lead_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lead_number IS NULL THEN
        NEW.lead_number := generate_sequential_number('LEAD-', 'leads', 'lead_number');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_opportunity_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.opportunity_number IS NULL THEN
        NEW.opportunity_number := generate_sequential_number('OPP-', 'opportunities', 'opportunity_number');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL THEN
        NEW.ticket_number := generate_sequential_number('TKT-', 'tickets', 'ticket_number');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invoice_number IS NULL THEN
        NEW.invoice_number := generate_sequential_number('INV-', 'invoices', 'invoice_number');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the triggers
DROP TRIGGER IF EXISTS trigger_generate_customer_number ON customers;
CREATE TRIGGER trigger_generate_customer_number
    BEFORE INSERT ON customers
    FOR EACH ROW
    EXECUTE FUNCTION generate_customer_number();

DROP TRIGGER IF EXISTS trigger_generate_lead_number ON leads;
CREATE TRIGGER trigger_generate_lead_number
    BEFORE INSERT ON leads
    FOR EACH ROW
    EXECUTE FUNCTION generate_lead_number();

DROP TRIGGER IF EXISTS trigger_generate_opportunity_number ON opportunities;
CREATE TRIGGER trigger_generate_opportunity_number
    BEFORE INSERT ON opportunities
    FOR EACH ROW
    EXECUTE FUNCTION generate_opportunity_number();

DROP TRIGGER IF EXISTS trigger_generate_ticket_number ON tickets;
CREATE TRIGGER trigger_generate_ticket_number
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION generate_ticket_number();

DROP TRIGGER IF EXISTS trigger_generate_invoice_number ON invoices;
CREATE TRIGGER trigger_generate_invoice_number
    BEFORE INSERT ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION generate_invoice_number();

-- Create audit trail functions
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, record_id, operation, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), NEW.created_by_id, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), NEW.updated_by_id, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, operation, old_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), OLD.updated_by_id, NOW());
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO crm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crm_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO crm_user;

-- Create database statistics update function
CREATE OR REPLACE FUNCTION update_table_statistics()
RETURNS VOID AS $$
BEGIN
    -- Update customer segments with current counts
    UPDATE customer_segments SET 
        customer_count = (
            SELECT COUNT(*) 
            FROM customers 
            WHERE segment_id = customer_segments.id
        ),
        last_calculated_at = NOW();
    
    -- Update lead source metrics
    UPDATE lead_sources SET
        total_leads = (
            SELECT COUNT(*)
            FROM leads
            WHERE source_id = lead_sources.id
        ),
        qualified_leads = (
            SELECT COUNT(*)
            FROM leads
            WHERE source_id = lead_sources.id AND status IN ('qualified', 'converted')
        ),
        converted_leads = (
            SELECT COUNT(*)
            FROM leads
            WHERE source_id = lead_sources.id AND status = 'converted'
        );
        
    -- Calculate conversion rates
    UPDATE lead_sources SET
        conversion_rate = CASE 
            WHEN total_leads > 0 THEN (converted_leads::DECIMAL / total_leads::DECIMAL) * 100
            ELSE 0
        END;
END;
$$ LANGUAGE plpgsql;

-- Schedule the statistics update (this would typically be done via a job scheduler)
-- For now, we'll just create the function that can be called manually or via cron

COMMIT;