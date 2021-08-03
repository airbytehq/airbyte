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
