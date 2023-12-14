CREATE
    SCHEMA COCKROACHDB_BASIC;

CREATE
    TYPE mood AS ENUM(
        'sad',
        'ok',
        'happy'
    );

CREATE
    TABLE
        COCKROACHDB_BASIC.TEST_DATASET(
            id INTEGER PRIMARY KEY,
            test_column_11 CHARACTER,
            test_column_12 CHARACTER(8),
            test_column_13 VARCHAR,
            test_column_14 CHARACTER(12),
            test_column_15 DATE,
            test_column_16 float8,
            test_column_17 FLOAT,
            test_column_19 INT,
            test_column_2 BIT(3),
            test_column_23 NUMERIC,
            test_column_24 DECIMAL,
            test_column_25 SMALLINT,
            test_column_26 text,
            test_column_27 TIME,
            test_column_28 timetz,
            test_column_29 TIMESTAMP,
            test_column_3 BIGINT,
            test_column_8 BOOLEAN
        );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        1,
        'a',
        '{asb123}',
        'a',
        'a',
        '1999-01-08',
        '123',
        '123',
        - 2147483648,
        B'101',
        '99999',
        '+inf',
        - 32768,
        'a',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54',
        - 9223372036854775808,
        TRUE
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        2,
        '*',
        '{asb12}',
        'abc',
        'abc',
        '1999-01-08',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        B'101',
        '99999',
        999,
        32767,
        'abc',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        9223372036854775807,
        'yes'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        3,
        '*',
        '{asb12}',
        'Миші йдуть на південь, не питай чому;',
        'Миші йдуть;',
        '1999-01-08',
        'infinity',
        'infinity',
        2147483647,
        B'101',
        '99999',
        '-inf',
        32767,
        'Миші йдуть;',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '1'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        4,
        '*',
        '{asb12}',
        '櫻花分店',
        '櫻花分店',
        '1999-01-08',
        '+infinity',
        '+infinity',
        2147483647,
        B'101',
        '99999',
        '+infinity',
        32767,
        '櫻花分店',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        FALSE
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        5,
        '*',
        '{asb12}',
        '',
        '',
        '1999-01-08',
        '+inf',
        '+inf',
        2147483647,
        B'101',
        '99999',
        '-infinity',
        32767,
        '',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        'no'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        6,
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '',
        '1999-01-08',
        'inf',
        'inf',
        2147483647,
        B'101',
        '99999',
        'nan',
        32767,
        '\xF0\x9F\x9A\x80',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '0'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        7,
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '',
        '1999-01-08',
        '-inf',
        '-inf',
        2147483647,
        B'101',
        '99999',
        'nan',
        32767,
        '\xF0\x9F\x9A\x80',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '0'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        8,
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '',
        '1999-01-08',
        '-infinity',
        '-infinity',
        2147483647,
        B'101',
        '99999',
        'nan',
        32767,
        '\xF0\x9F\x9A\x80',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '0'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        9,
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '',
        '1999-01-08',
        'nan',
        'nan',
        2147483647,
        B'101',
        '99999',
        'nan',
        32767,
        '\xF0\x9F\x9A\x80',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '0'
    );

INSERT
    INTO
        COCKROACHDB_BASIC.TEST_DATASET
    VALUES(
        10,
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '',
        '1999-01-08',
        'nan',
        'nan',
        2147483647,
        B'101',
        '99999',
        'nan',
        32767,
        '\xF0\x9F\x9A\x80',
        '04:05:06',
        '04:05:06Z',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        '0'
    );
