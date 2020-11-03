CREATE
    TABLE
        id_and_name(
            id INTEGER,
            name VARCHAR(200)
        );

-- Add UTF characters to make sure the tap can read UTF
 INSERT
    INTO
        id_and_name(
            id,
            name
        )
    VALUES(
        1,
        E'\u2013 someutfstring'
    ),
    (
        2,
        E'\u2215'
    );
