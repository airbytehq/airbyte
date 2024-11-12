CREATE
    DATABASE MYSQL_BASIC;

USE MYSQL_BASIC;
SET
@@sql_mode = '';

CREATE
    TABLE
        test.TEST_DATASET(
            id INTEGER PRIMARY KEY,
            test_column_1 bit,
            test_column_10 SMALLINT,
            test_column_12 SMALLINT unsigned,
            test_column_13 mediumint,
            test_column_15 INT,
            test_column_16 INT unsigned,
            test_column_18 BIGINT,
            test_column_19 FLOAT,
            test_column_2 bit(1),
            test_column_20 DOUBLE,
            test_column_21 DECIMAL(
                10,
                3
            ),
            test_column_22 DECIMAL(
                19,
                2
            ),
            test_column_24 DATE,
            test_column_25 datetime NOT NULL DEFAULT now(),
            test_column_26 datetime,
            test_column_27 TIMESTAMP,
            test_column_29 TIME,
            test_column_3 bit(7),
            test_column_30 YEAR,
            test_column_31 VARCHAR(63),
            test_column_4 tinyint,
            test_column_5 tinyint(1),
            test_column_6 tinyint(1) unsigned,
            test_column_7 tinyint(2),
            test_column_8 BOOL,
            test_column_9 BOOLEAN
        );

INSERT
    INTO
        test.TEST_DATASET
    VALUES(
        1,
        1,
        - 32768,
        0,
        - 8388608,
        - 2147483648,
        3428724653,
        9223372036854775807,
        10.5,
        1,
        POWER( 10, 308 ),
        0.188,
        1700000.01,
        '1999-01-08',
        '2005-10-10 23:22:21',
        '2005-10-10 23:22:21',
        '2021-01-00',
        '-22:59:59',
        b'1000001',
        '1997',
        'Airbyte',
        - 128,
        1,
        0,
        - 128,
        1,
        1
    );

INSERT
    INTO
        test.TEST_DATASET
    VALUES(
        2,
        0,
        32767,
        65535,
        8388607,
        2147483647,
        3428724653,
        9223372036854775807,
        10.5,
        0,
        1 / POWER( 10, 45 ),
        0.188,
        1700000.01,
        '2021-01-01',
        '2013-09-05T10:10:02',
        '2013-09-05T10:10:02',
        '2021-00-00',
        '23:59:59',
        b'1000001',
        '0',
        '!"#$%&\'()*+,
        -./:;

<=>? \@ [ \ ] ^_\ ` { | } ~ ', 127, 0, 1, 127, 0, 0);
INSERT INTO test.TEST_DATASET VALUES (3, 0, 32767, 65535, 8388607, 2147483647, 3428724653, 9223372036854775807, 10.5, 0, 10.5, 0.188, 1700000.01, ' 2021 - 01 - 01 ', ' 2013 - 09 - 06 T10:10:02 ', ' 2013 - 09 - 06 T10:10:02 ', ' 0000 - 00 - 00 ', ' 00:00:00 ', b' 1000001 ', ' 50 ', ' ! "#$%&\'()*+,-./:;<=>?\@[\]^_\`{|}~', 127, 0, 2, 127, 0, 0);
INSERT INTO test.TEST_DATASET VALUES (4, 0, 32767, 65535, 8388607, 2147483647, 3428724653, 9223372036854775807, 10.5, 0, 10.5, 0.188, 1700000.01, '2021-01-01', '2013-09-06T10:10:02', '2013-09-06T10:10:02', '2022-08-09T10:17:16.161342Z', '00:00:00', b'1000001', '70', '!" #$ %& \'()*+,-./:;<=>?\@[\]^_\`{|}~',
127,
0,
3,
127,
0,
0
    );

INSERT
    INTO
        test.TEST_DATASET
    VALUES(
        5,
        0,
        32767,
        65535,
        8388607,
        2147483647,
        3428724653,
        9223372036854775807,
        10.5,
        0,
        10.5,
        0.188,
        1700000.01,
        '2021-01-01',
        '2013-09-06T10:10:02',
        '2013-09-06T10:10:02',
        '2022-08-09T10:17:16.161342Z',
        '00:00:00',
        b'1000001',
        '80',
        '!"#$%&\'()*+,
        -./:;

<=>? \@ [ \ ] ^_\ ` { | } ~ ', 127, 0, 3, 127, 0, 0);
INSERT INTO test.TEST_DATASET VALUES (6, 0, 32767, 65535, 8388607, 2147483647, 3428724653, 9223372036854775807, 10.5, 0, 10.5, 0.188, 1700000.01, ' 2021 - 01 - 01 ', ' 2013 - 09 - 06 T10:10:02 ', ' 2013 - 09 - 06 T10:10:02 ', ' 2022 - 08 - 09 T10:17:16.161342 Z', ' 00:00:00 ', b' 1000001 ', ' 99 ', ' ! "#$%&\'()*+,-./:;<=>?\@[\]^_\`{|}~', 127, 0, 3, 127, 0, 0);
INSERT INTO test.TEST_DATASET VALUES (7, 0, 32767, 65535, 8388607, 2147483647, 3428724653, 9223372036854775807, 10.5, 0, 10.5, 0.188, 1700000.01, '2021-01-01', '2013-09-06T10:10:02', '2013-09-06T10:10:02', '2022-08-09T10:17:16.161342Z', '00:00:00', b'1000001', '99', '!" #$ %& \'()*+,-./:;<=>?\@[\]^_\`{|}~',
127,
0,
3,
127,
0,
0
    );