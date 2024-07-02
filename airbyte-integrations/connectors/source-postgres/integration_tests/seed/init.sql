-- Enable the uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Variables to hold the current date and generated UUID
DO $$ 
DECLARE
schema_name TEXT;
BEGIN 
    -- Generate the schema name in 'date-uuid' format
    schema_name := to_char(CURRENT_DATE, 'YYYYMMDD') || '-' || uuid_generate_v4();

    -- Create schema with the dynamic name
EXECUTE format('CREATE SCHEMA %I', schema_name);

-- Create a table within the dynamically named schema
EXECUTE format('
        CREATE TABLE %I.id_and_name (
            id SERIAL PRIMARY KEY,
            name INT NOT NULL,
        )', schema_name);

-- Insert sample data into the table
EXECUTE format('INSERT INTO %I.my_table VALUES ($1, $2)', schema_name) USING '1', 'picard';
EXECUTE format('INSERT INTO %I.my_table VALUES ($1, $2)', schema_name) USING '2', 'crusher';
END $$;