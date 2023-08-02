CREATE
    TABLE
        ` sat_test_dataset.sat_basic_dataset `(
            id NUMERIC(29),
            test_column_1 int64,
            test_column_10 DECIMAL(
                29,
                9
            ),
            test_column_11 bigdecimal(
                76,
                38
            ),
            test_column_12 float64,
            test_column_13 bool,
            test_column_15 DATE,
            test_column_16 datetime,
            test_column_17 TIMESTAMP,
            test_column_19 string,
            test_column_2 INT,
            test_column_21 TIME,
            test_column_3 SMALLINT,
            test_column_4 INTEGER,
            test_column_5 BIGINT,
            test_column_6 tinyint,
            test_column_7 byteint,
            test_column_8 NUMERIC(
                29,
                9
            ),
            test_column_9 bignumeric(
                76,
                38
            )
        );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        1,
        - 128,
        - 128,
        - 128,
        - 128,
        TRUE,
        DATE('2021-10-20'),
        datetime('2021-10-20 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'qwe',
        - 128,
        TIME(
            15,
            30,
            00
        ),
        - 128,
        - 128,
        - 128,
        - 128,
        - 128,
        - 128,
        - 128
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        2,
        127,
        127,
        127,
        127,
        FALSE,
        DATE('9999-12-31'),
        datetime('9999-12-31 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        127,
        127
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        3,
        9223372036854775807,
        999999999999999999,
        999999999999999999,
        0.123456789,
        FALSE,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        999999999999999999,
        999999999999999999
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        4,
        - 9223372036854775808,
        - 999999999999999999,
        - 999999999999999999,
        - 0.123456789,
        FALSE,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        - 999999999999999999,
        - 999999999999999999
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        5,
        - 9223372036854775808,
        0.123456789,
        0.123456789,
        - 0.123456789,
        FALSE,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        0.123456789,
        0.123456789
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        6,
        - 9223372036854775808,
        - 0.123456789,
        - 0.123456789,
        - 0.123456789,
        FALSE,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        - 0.123456789,
        - 0.123456789
    );

INSERT
    INTO
        sat_test_dataset.sat_basic_dataset
    VALUES(
        7,
        - 9223372036854775808,
        - 0.123456789,
        - 0.123456789,
        - 0.123456789,
        FALSE,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        'йцу',
        127,
        TIME(
            15,
            30,
            00
        ),
        127,
        127,
        127,
        127,
        127,
        - 0.123456789,
        - 0.123456789
    );
