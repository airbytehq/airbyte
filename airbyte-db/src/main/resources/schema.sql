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
        'incomplete',
        'failed',
        'succeeded',
        'cancelled'
    );

CREATE
    TYPE ATTEMPT_STATUS AS ENUM(
        'running',
        'failed',
        'succeeded'
    );

CREATE
    TYPE JOB_CONFIG_TYPE AS ENUM(
        'check_connection_source',
        'check_connection_destination',
        'discover_schema',
        'get_spec',
        'sync',
        'reset_connection'
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
            config_type JOB_CONFIG_TYPE,
            SCOPE VARCHAR(255),
            config JSONB,
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
            attempt_number INTEGER,
            log_path VARCHAR(255),
            OUTPUT JSONB,
            status ATTEMPT_STATUS,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ,
            ended_at TIMESTAMPTZ
        );

CREATE
    UNIQUE INDEX job_attempt_idx ON
    ATTEMPTS(
        job_id,
        attempt_number
    );

-- entries
 INSERT
    INTO
        AIRBYTE_METADATA
    VALUES(
        'server_uuid',
        uuid_generate_v4()
    );

-- grants
 GRANT ALL ON
DATABASE airbyte TO docker;
