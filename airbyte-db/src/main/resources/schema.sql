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
    TYPE CANCELLATION_REASON AS ENUM(
        'too_many_failures',
        'user_requested'
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
            status JOB_STATUS,
            cancellation_reason CANCELLATION_REASON,
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
            log_path VARCHAR(255),
            OUTPUT JSONB,
            status ATTEMPT_STATUS,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ,
            -- todo auto update
 ended_at TIMESTAMPTZ
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
