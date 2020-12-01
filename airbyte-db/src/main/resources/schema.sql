-- database
 CREATE
    DATABASE airbyte;

\connect airbyte;

-- extensions
 CREATE
    EXTENSION IF NOT EXISTS "uuid-ossp";

-- types
 CREATE
    TYPE JOB_STATUS AS ENUM(
        'pending',
        'running',
        'failed',
        'completed',
        'cancelled'
    );

CREATE
    TYPE ATTEMPT_STATUS AS ENUM(
        'running',
        'failed',
        'completed'
    );

-- tables
 CREATE
    TABLE
        AIRBYTE_METADATA(
            KEY VARCHAR(255) PRIMARY KEY,
            value VARCHAR(255)
        );

CREATE
    TABLE
        JOBS(
            id BIGSERIAL PRIMARY KEY,
            SCOPE VARCHAR(255),
            config JSONB,
            --             log_path VARCHAR(255),
 --             OUTPUT JSONB,
 --             attempts INTEGER,
 status JOB_STATUS,
            started_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ
        );

CREATE
    TABLE
        ATTEMPTS(
            id BIGSERIAL PRIMARY KEY,
            job_id BIGSERIAL,
            attempt_id BIGSERIAL,
            --             SCOPE VARCHAR(255),
 --             config JSONB,
 log_path VARCHAR(255),
            OUTPUT JSONB,
            --             attempts INTEGER,
 status ATTEMPT_STATUS,
            started_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ -- todo auto update
        );

-- entries
 INSERT
    INTO
        AIRBYTE_METADATA
    VALUES(
        'server-uuid',
        uuid_generate_v4()
    );

-- grants
 GRANT ALL ON
DATABASE airbyte TO docker;
