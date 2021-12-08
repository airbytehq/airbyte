CREATE
    TYPE "source_type" AS enum(
        'api',
        'file',
        'database',
        'custom'
    );

CREATE
    TYPE "actor_type" AS enum(
        'source',
        'destination'
    );

CREATE
    TYPE "operator_type" AS enum(
        'normalization',
        'dbt'
    );

CREATE
    TYPE "namespace_definition_type" AS enum(
        'source',
        'destination',
        'customformat'
    );

CREATE
    TYPE "status_type" AS enum(
        'active',
        'inactive',
        'deprecated'
    );

CREATE
    TABLE
        IF NOT EXISTS "workspace"(
            id uuid NOT NULL,
            customer_id uuid NULL,
            name VARCHAR(256) NOT NULL,
            slug VARCHAR(256) NOT NULL,
            email VARCHAR(256) NULL,
            initial_setup_complete BOOLEAN NOT NULL,
            anonymous_data_collection BOOLEAN NULL,
            news BOOLEAN NULL,
            security_updates BOOLEAN NULL,
            display_setup_wizard BOOLEAN NULL,
            tombstone BOOLEAN NOT NULL DEFAULT FALSE,
            notifications jsonb NULL,
            first_completed_sync BOOLEAN NULL,
            feedback_done BOOLEAN NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id)
        );

CREATE
    TABLE
        IF NOT EXISTS "actor_definition"(
            id uuid NOT NULL,
            name VARCHAR(256) NOT NULL,
            docker_repository VARCHAR(256) NOT NULL,
            docker_image_tag VARCHAR(256) NOT NULL,
            documentation_url VARCHAR(256) NULL,
            icon VARCHAR(256) NULL,
            actor_type actor_type NOT NULL,
            source_type source_type NULL,
            spec jsonb NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id)
        );

CREATE
    TABLE
        IF NOT EXISTS "actor"(
            id uuid NOT NULL,
            workspace_id uuid NOT NULL,
            actor_definition_id uuid NOT NULL,
            name VARCHAR(256) NOT NULL,
            configuration jsonb NOT NULL,
            actor_type actor_type NOT NULL,
            tombstone BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id),
            FOREIGN KEY(workspace_id) REFERENCES "workspace"("id"),
            FOREIGN KEY(actor_definition_id) REFERENCES "actor_definition"("id")
        );

CREATE
    INDEX "actor_actor_definition_id_idx" ON
    "actor"("actor_definition_id");

CREATE
    TABLE
        IF NOT EXISTS "actor_oauth_parameter"(
            id uuid NOT NULL,
            workspace_id uuid NULL,
            actor_definition_id uuid NOT NULL,
            configuration jsonb NOT NULL,
            actor_type actor_type NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id),
            FOREIGN KEY(workspace_id) REFERENCES "workspace"("id"),
            FOREIGN KEY(actor_definition_id) REFERENCES "actor_definition"("id")
        );

CREATE
    TABLE
        IF NOT EXISTS "operation"(
            id uuid NOT NULL,
            workspace_id uuid NOT NULL,
            name VARCHAR(256) NOT NULL,
            operator_type operator_type NOT NULL,
            operator_normalization jsonb NULL,
            operator_dbt jsonb NULL,
            tombstone BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id),
            FOREIGN KEY(workspace_id) REFERENCES "workspace"("id")
        );

CREATE
    TABLE
        IF NOT EXISTS "connection"(
            id uuid NOT NULL,
            namespace_definition namespace_definition_type NOT NULL,
            namespace_format VARCHAR(256) NULL,
            prefix VARCHAR(256) NULL,
            source_id uuid NOT NULL,
            destination_id uuid NOT NULL,
            name VARCHAR(256) NOT NULL,
            CATALOG jsonb NOT NULL,
            status status_type NULL,
            schedule jsonb NULL,
            manual BOOLEAN NOT NULL,
            resource_requirements jsonb NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(id),
            FOREIGN KEY(source_id) REFERENCES "actor"("id"),
            FOREIGN KEY(destination_id) REFERENCES "actor"("id")
        );

CREATE
    INDEX "connection_source_id_idx" ON
    "connection"("source_id");

CREATE
    INDEX "connection_destination_id_idx" ON
    "connection"("destination_id");

CREATE
    TABLE
        IF NOT EXISTS "connection_operation"(
            id uuid NOT NULL,
            connection_id uuid NOT NULL,
            operation_id uuid NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(
                id,
                connection_id,
                operation_id
            ),
            FOREIGN KEY(connection_id) REFERENCES "connection"("id"),
            FOREIGN KEY(operation_id) REFERENCES "operation"("id")
        );

CREATE
    TABLE
        IF NOT EXISTS "state"(
            id uuid NOT NULL,
            connection_id uuid NOT NULL,
            state jsonb NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CAST(
                CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE
            ),
            PRIMARY KEY(
                id,
                connection_id
            ),
            FOREIGN KEY(connection_id) REFERENCES "connection"("id")
        );
