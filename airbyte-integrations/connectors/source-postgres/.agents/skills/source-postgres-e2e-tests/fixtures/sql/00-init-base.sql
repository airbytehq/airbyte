-- Idempotent base init for source-postgres e2e tests (non-CDC).
-- The test_db database is created by the container (POSTGRES_DB); this
-- fixture just (re)creates a small public.sample table with three rows.

DROP TABLE IF EXISTS public.sample;

CREATE TABLE public.sample (
  id    INTEGER     NOT NULL PRIMARY KEY,
  label VARCHAR(64) NOT NULL
);

INSERT INTO public.sample (id, label) VALUES
  (1, 'alpha'),
  (2, 'beta'),
  (3, 'gamma');
