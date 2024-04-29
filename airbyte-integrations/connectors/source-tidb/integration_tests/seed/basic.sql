CREATE
    TABLE
        id_and_name(
            id INTEGER,
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
        'picard'
    ),
    (
        2,
        'crusher'
    ),
    (
        3,
        'vash'
    );

CREATE
    TABLE
        starships(
            id INTEGER,
            name VARCHAR(200)
        );

INSERT
    INTO
        starships(
            id,
            name
        )
    VALUES(
        1,
        'enterprise-d'
    ),
    (
        2,
        'defiant'
    ),
    (
        3,
        'yamato'
    );
