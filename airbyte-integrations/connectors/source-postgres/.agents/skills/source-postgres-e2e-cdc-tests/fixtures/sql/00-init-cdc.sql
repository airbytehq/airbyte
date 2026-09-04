-- Initialize the PostgreSQL logical replication CDC fixture.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_replication_slots
    WHERE slot_name = 'airbyte_slot'
  ) THEN
    PERFORM pg_drop_replication_slot('airbyte_slot');
  END IF;
END
$$;

DROP PUBLICATION IF EXISTS airbyte_publication;
DROP TABLE IF EXISTS public.users;

CREATE TABLE public.users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  email VARCHAR(200) NOT NULL
);

INSERT INTO public.users (name, email) VALUES
  ('alice', 'alice@example.com'),
  ('bob', 'bob@example.com'),
  ('carol', 'carol@example.com');

CREATE PUBLICATION airbyte_publication FOR TABLE public.users;
SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
