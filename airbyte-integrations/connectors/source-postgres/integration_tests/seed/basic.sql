CREATE
    SCHEMA POSTGRES_BASIC;

CREATE
    TYPE mood AS ENUM(
        'sad',
        'ok',
        'happy'
    );

CREATE
    TYPE inventory_item AS(
        name text,
        supplier_id INTEGER,
        price NUMERIC
    );
SET
lc_monetary TO 'en_US.utf8';
SET
TIMEZONE TO 'MST';

CREATE
    EXTENSION hstore;

CREATE
    TABLE
        POSTGRES_BASIC.TEST_DATASET(
            id INTEGER PRIMARY KEY,
            test_column_1 BIGINT,
            test_column_11 CHAR,
            test_column_12 CHAR(8),
            test_column_13 CHARACTER,
            test_column_14 CHARACTER(8),
            test_column_15 text,
            test_column_16 VARCHAR,
            test_column_20 DATE NOT NULL DEFAULT now(),
            test_column_21 DATE,
            test_column_23 FLOAT,
            test_column_24 DOUBLE PRECISION,
            test_column_27 INT,
            test_column_28 INTEGER,
            test_column_3 BIT(1),
            test_column_4 BIT(3),
            test_column_44 REAL,
            test_column_46 SMALLINT,
            test_column_51 TIME WITHOUT TIME ZONE,
            test_column_52 TIME,
            test_column_53 TIME WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            test_column_54 TIMESTAMP,
            test_column_55 TIMESTAMP WITHOUT TIME ZONE,
            test_column_56 TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
            test_column_57 TIMESTAMP,
            test_column_58 TIMESTAMP WITHOUT TIME ZONE,
            test_column_59 TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            test_column_60 TIMESTAMP WITH TIME ZONE,
            test_column_61 timestamptz,
            test_column_7 bool,
            test_column_70 TIME WITH TIME ZONE,
            test_column_71 timetz,
            test_column_8 BOOLEAN
        );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        1,
        - 9223372036854775808,
        'a',
        '{asb123}',
        'a',
        '{asb123}',
        'a',
        'a',
        '1999-01-08',
        '1999-01-08',
        '123',
        '123',
        1001,
        1001,
        B'0',
        B'101',
        3.4145,
        - 32768,
        '13:00:01',
        '13:00:01',
        '13:00:01',
        TIMESTAMP '2004-10-19 10:23:00',
        TIMESTAMP '2004-10-19 10:23:00',
        TIMESTAMP '2004-10-19 10:23:00',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:00-08',
        TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:00-08',
        TRUE,
        '13:00:01',
        '13:00:01',
        TRUE
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        2,
        9223372036854775807,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        'abc',
        'abc',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        - 2147483648,
        - 2147483648,
        B'0',
        B'101',
        3.4145,
        32767,
        '13:00:02+8',
        '13:00:02+8',
        '13:00:02+8',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        TIMESTAMP '2004-10-19 10:23:54.123456',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54.123456-08',
        TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54.123456-08',
        'yes',
        '13:00:00+8',
        '13:00:00+8',
        'yes'
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        3,
        0,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        'Миші йдуть на південь, не питай чому;',
        'Миші йдуть на південь, не питай чому;',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        2147483647,
        B'0',
        B'101',
        3.4145,
        32767,
        '13:00:03-8',
        '13:00:03-8',
        '13:00:03-8',
        TIMESTAMP '3004-10-19 10:23:54.123456 BC',
        TIMESTAMP '3004-10-19 10:23:54.123456 BC',
        TIMESTAMP '3004-10-19 10:23:54.123456 BC',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '3004-10-19 10:23:54.123456-08 BC',
        TIMESTAMP WITH TIME ZONE '3004-10-19 10:23:54.123456-08 BC',
        '1',
        '13:00:03-8',
        '13:00:03-8',
        '1'
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        4,
        0,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        '櫻花分店',
        '櫻花分店',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        2147483647,
        B'0',
        B'101',
        3.4145,
        32767,
        '13:00:04Z',
        '13:00:04Z',
        '13:00:04Z',
        TIMESTAMP '0001-01-01 00:00:00.000000',
        TIMESTAMP '0001-01-01 00:00:00.000000',
        TIMESTAMP '0001-01-01 00:00:00.000000',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '0001-12-31 16:00:00.000000-08 BC',
        TIMESTAMP WITH TIME ZONE '0001-12-31 16:00:00.000000-08 BC',
        FALSE,
        '13:00:04Z',
        '13:00:04Z',
        FALSE
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        5,
        0,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        '',
        '',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        2147483647,
        B'0',
        B'101',
        3.4145,
        32767,
        '13:00:05.01234Z+8',
        '13:00:05.01234Z+8',
        '13:00:05.01234Z+8',
        TIMESTAMP '0001-12-31 23:59:59.999999 BC',
        TIMESTAMP '0001-12-31 23:59:59.999999 BC',
        TIMESTAMP '0001-12-31 23:59:59.999999 BC',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        'no',
        '13:00:05.012345Z+8',
        '13:00:05.012345Z+8',
        'no'
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        6,
        0,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '\xF0\x9F\x9A\x80',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        2147483647,
        B'0',
        B'101',
        3.4145,
        32767,
        '13:00:00Z-8',
        '13:00:00Z-8',
        '13:00:00Z-8',
        'epoch',
        'epoch',
        'epoch',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        '0',
        '13:00:06.00000Z-8',
        '13:00:06.00000Z-8',
        '0'
    );

INSERT
    INTO
        POSTGRES_BASIC.TEST_DATASET
    VALUES(
        7,
        0,
        '*',
        '{asb12}',
        '*',
        '{asb12}',
        '\xF0\x9F\x9A\x80',
        '\xF0\x9F\x9A\x80',
        '1991-02-10 BC',
        '1991-02-10 BC',
        '1234567890.1234567',
        '1234567890.1234567',
        2147483647,
        2147483647,
        B'0',
        B'101',
        3.4145,
        32767,
        '24:00:00',
        '24:00:00',
        '24:00:00',
        'epoch',
        'epoch',
        'epoch',
        0,
        0,
        0,
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC',
        '0',
        '13:00:06.00000Z-8',
        '13:00:06.00000Z-8',
        '0'
    );
