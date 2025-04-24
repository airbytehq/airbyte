CREATE
    TABLE
        IF NOT EXISTS sat_test_dataset.sat_basic_dataset(
            id INTEGER,
            test_column_1 SMALLINT,
            test_column_2 INTEGER,
            test_column_3 BIGINT,
            test_column_4 DECIMAL,
            test_column_5 REAL,
            test_column_6 DOUBLE PRECISION,
            test_column_7 BOOLEAN,
            test_column_8 CHAR,
            test_column_9 VARCHAR,
            test_column_10 DATE,
            test_column_11 TIMESTAMP,
            test_column_12 TIMESTAMPTZ,
            test_column_13 TIME,
            test_column_14 TIMETZ,
            test_column_15 VARBYTE
        );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        1,
        1,
        126,
        1024,
        555.666,
        777.888,
        999.000,
        TRUE,
        'q',
        'some text',
        '2008-12-31',
        'Jun 1,2008  09:59:59',
        'Jun 1,2008 09:59:59 EST',
        '04:05:06',
        '04:05:06 EST',
        'xxx'::varbyte
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        2,
        - 5,
        - 126,
        - 1024,
        - 555.666,
        - 777.888,
        - 999.000,
        FALSE,
        'g',
        'new text',
        '1987-10-10',
        'Jun 21,2005  12:00:59',
        'Oct 15,2003 09:59:59 EST',
        '04:05:00',
        '04:05:00 EST',
        'yyy'::varbyte
    );
