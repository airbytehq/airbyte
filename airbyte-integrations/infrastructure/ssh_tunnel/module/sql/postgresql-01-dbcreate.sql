-- generic setup for a brand new empty postgresql RDS
CREATE
    ROLE integrationtest_rw;

GRANT integrationtest_rw TO airbyte;

CREATE
    DATABASE test OWNER integrationtest_rw;

GRANT CONNECT ON
DATABASE test TO integrationtest_rw;

CREATE
    SCHEMA integrationtest AUTHORIZATION integrationtest_rw;

GRANT USAGE,
CREATE
    ON
    SCHEMA integrationtest TO integrationtest_rw;

GRANT SELECT
    ,
    INSERT
        ,
        UPDATE
            ,
            DELETE
                ON
                ALL TABLES IN SCHEMA integrationtest TO integrationtest_rw;

ALTER DEFAULT PRIVILEGES IN SCHEMA integrationtest GRANT SELECT
    ,
    INSERT
        ,
        UPDATE
            ,
            DELETE
                ON
                TABLES TO integrationtest_rw;

GRANT USAGE ON
ALL SEQUENCES IN SCHEMA integrationtest TO integrationtest_rw;

ALTER DEFAULT PRIVILEGES IN SCHEMA integrationtest GRANT USAGE ON
SEQUENCES TO integrationtest_rw;

REVOKE ALL ON
database template1
FROM
public;

REVOKE ALL ON
database postgres
FROM
public;

# Test DATA used BY the postgres SOURCE test classes
SET
SCHEMA 'public';

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
