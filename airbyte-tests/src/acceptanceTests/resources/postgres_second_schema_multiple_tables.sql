CREATE
    SCHEMA staging;

CREATE
    TABLE
        staging.cool_employees(
            id INTEGER NOT NULL,
            name VARCHAR(200)
        );

INSERT
    INTO
        staging.cool_employees(
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
        staging.awesome_people(
            id INTEGER NOT NULL,
            name VARCHAR(200)
        );

INSERT
    INTO
        staging.awesome_people(
            id,
            name
        )
    VALUES(
        1,
        'davin'
    ),
    (
        2,
        'chris'
    );
