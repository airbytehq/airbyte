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
    TABLE
        color_palette(
            id INTEGER PRIMARY KEY,
            color VARCHAR(200)
        );

INSERT
    INTO
        color_palette(
            id,
            color
        )
    VALUES(
        1,
        'red'
    ),
    (
        2,
        'blue'
    ),
    (
        3,
        'green'
    );

CREATE
    ROLE airbyte_role REPLICATION LOGIN;

ALTER TABLE
    id_and_name REPLICA IDENTITY DEFAULT;

ALTER TABLE
    color_palette REPLICA IDENTITY DEFAULT;

CREATE
    PUBLICATION airbyte_publication FOR TABLE
        id_and_name,
        color_palette;

SELECT
    pg_create_logical_replication_slot(
        'airbyte_slot',
        'pgoutput'
    );
