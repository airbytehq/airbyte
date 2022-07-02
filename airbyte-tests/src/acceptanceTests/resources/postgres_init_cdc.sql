CREATE
    TABLE
        id_and_name(
            id INTEGER PRIMARY KEY,
            name VARCHAR(200)
        );

INSERT
    INTO
        id_and_name(
            id,
            name
        )
    VALUES(
        1,
        'sherif'
    ),
    (
        2,
        'charles'
    ),
    (
        3,
        'jared'
    ),
    (
        4,
        'michel'
    ),
    (
        5,
        'john'
    );

CREATE
    ROLE airbyte_role REPLICATION LOGIN;

ALTER TABLE
    id_and_name REPLICA IDENTITY DEFAULT;

CREATE
    PUBLICATION airbyte_publication FOR TABLE
        id_and_name;

SELECT
    pg_create_logical_replication_slot(
        'airbyte_slot',
        'pgoutput'
    );
