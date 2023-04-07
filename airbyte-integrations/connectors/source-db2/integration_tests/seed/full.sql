CREATE
    SCHEMA DB2_FULL;

CREATE
    TABLE
        DB2_FULL.TEST_DATASET(
            ID INTEGER NOT NULL PRIMARY KEY,
            TEST_COLUMN_1 SMALLINT,
            TEST_COLUMN_10 BOOLEAN,
            TEST_COLUMN_11 CHAR,
            TEST_COLUMN_12 VARCHAR(256),
            TEST_COLUMN_13 VARCHAR(128),
            TEST_COLUMN_14 NCHAR,
            TEST_COLUMN_15 NVARCHAR(128),
            TEST_COLUMN_16 GRAPHIC(8),
            TEST_COLUMN_17 VARGRAPHIC(8),
            TEST_COLUMN_18 VARBINARY(32),
            TEST_COLUMN_19 BLOB,
            TEST_COLUMN_2 INTEGER,
            TEST_COLUMN_20 CLOB,
            TEST_COLUMN_21 NCLOB,
            TEST_COLUMN_22 XML,
            TEST_COLUMN_23 DATE,
            TEST_COLUMN_24 TIME,
            TEST_COLUMN_25 TIMESTAMP,
            TEST_COLUMN_3 BIGINT,
            TEST_COLUMN_4 DECIMAL(
                31,
                0
            ),
            TEST_COLUMN_5 REAL,
            TEST_COLUMN_6 DOUBLE,
            TEST_COLUMN_7 DECFLOAT(16),
            TEST_COLUMN_8 DECFLOAT(34),
            TEST_COLUMN_9 DECFLOAT
        );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        1,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        SNaN
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        2,
        - 32768,
        't',
        'a',
        'тест',
        chr(33)|| chr(34)|| chr(35)|| chr(36)|| chr(37)|| chr(38)|| chr(39)|| chr(40)|| chr(41),
        ' ',
        ' ',
        ' ',
        VARGRAPHIC(
            100500,
            ','
        ),
        VARBINARY(
            'test VARBINARY type',
            19
        ),
        BLOB(' '),
        - 2147483648,
        ' ',
        ' ',
        XMLPARSE(
            DOCUMENT '<?xml version="1.0"?><book><title>Manual</title><chapter>...</chapter></book>' PRESERVE WHITESPACE
        ),
        '0001-01-01',
        '00.00.00',
        '2018-03-22-12.00.00.123',
        - 9223372036854775808,
        1,
        0,
        DOUBLE('-1.7976931348623157E+308'),
        0,
        0,
        NaN
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        3,
        32767,
        'true',
        ' ',
        '⚡ test ��',
        NULL,
        'テ',
        'テスト',
        '12345678',
        NULL,
        NULL,
        BLOB('test BLOB type'),
        2147483647,
        CLOB('test CLOB type'),
        NCLOB('test NCLOB type'),
        NULL,
        '9999-12-31',
        '1:59 PM',
        '2018-03-22-12.00.00.123456',
        9223372036854775807,
        DECIMAL(
            (
                - 1 + 10E + 29
            ),
            31,
            0
        ),
        CAST(
            '-3.4028234663852886E38' AS REAL
        ),
        DOUBLE('-2.2250738585072014E-308'),
        1.0E308,
        DECFLOAT(
            10E + 307,
            34
        ),
        Infinity
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        4,
        NULL,
        'y',
        '*',
        '!"#$%&\''()*+,-./:;<=>?\@[\]^_\`{|}~',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        '23.59.59',
        '20180322125959',
        NULL,
        DECIMAL(
            (
                1 - 10E + 29
            ),
            31,
            0
        ),
        REAL('-1.1754943508222875e-38'),
        DOUBLE('2.2250738585072014E-308'),
        1.0E - 306,
        DECFLOAT(
            10E - 307,
            34
        ),
        - Infinity
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        5,
        NULL,
        'yes',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        '20180101 12:00:59 PM',
        NULL,
        NULL,
        REAL(
            1.1754943508222875e - 38
        ),
        DOUBLE('1.7976931348623157E+308'),
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        6,
        NULL,
        'on',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        3.4028234663852886E38,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        7,
        NULL,
        '1',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        8,
        NULL,
        'f',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        9,
        NULL,
        'false',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        10,
        NULL,
        'n',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        11,
        NULL,
        'no',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        12,
        NULL,
        'off',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT
    INTO
        DB2_FULL.TEST_DATASET
    VALUES(
        13,
        NULL,
        '0',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    );
