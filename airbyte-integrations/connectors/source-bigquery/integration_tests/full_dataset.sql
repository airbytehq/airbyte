CREATE
    TABLE
        sat_test_dataset.sat_full_dataset(
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
            test_column_14 bytes,
            test_column_15 DATE,
            test_column_16 datetime,
            test_column_17 TIMESTAMP,
            test_column_18 geography,
            test_column_19 string,
            test_column_2 INT,
            test_column_20 STRUCT < course STRING,
            id INT64 >,
            test_column_21 TIME,
            test_column_22 ARRAY <String>,
            test_column_23 STRUCT < frst String,
            sec int64,
            obbj STRUCT < id_col int64,
            mega_obbj STRUCT < last_col TIME >>>,
            test_column_24 ARRAY < STRUCT < fff String,
            ggg int64 >>,
            test_column_25 ARRAY < STRUCT < fff String,
            ggg ARRAY < STRUCT < ooo String,
            kkk int64 >>>>,
            test_column_26 INTERVAL,
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
        sat_test_dataset.sat_full_dataset
    VALUES(
        1,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        FROM_BASE64("test"),
        DATE('2021-10-20'),
        datetime('2021-10-20 11:22:33'),
        TIMESTAMP('2021-10-20 11:22:33'),
        ST_GEOGFROMTEXT('POINT(1 2)'),
        'qwe',
        NULL,
        STRUCT(
            "B.A",
            12
        ),
        TIME(
            15,
            30,
            00
        ),
        [ 'a',
        'b' ],
        STRUCT(
            's' AS frst,
            1 AS sec,
            STRUCT(
                555 AS id_col,
                STRUCT(
                    TIME(
                        15,
                        30,
                        00
                    ) AS TIME
                ) AS mega_obbj
            ) AS obbj
        ),
        [ STRUCT(
            'qqq' AS fff,
            1 AS ggg
        ),
        STRUCT(
            'kkk' AS fff,
            2 AS ggg
        )],
        [ STRUCT(
            'qqq' AS fff,
            [ STRUCT(
                'fff' AS ooo,
                1 AS kkk
            ),
            STRUCT(
                'hhh' AS ooo,
                2 AS kkk
            )] AS ggg
        )],
        MAKE_INTERVAL(
            2021,
            10,
            10,
            10,
            10,
            10
        ),
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
        sat_test_dataset.sat_full_dataset
    VALUES(
        2,
        - 128,
        - 128,
        - 128,
        - 128,
        FALSE,
        NULL,
        DATE('9999-12-31'),
        datetime('9999-12-31 11:22:33'),
        NULL,
        NULL,
        'йцу',
        - 128,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
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
        sat_test_dataset.sat_full_dataset
    VALUES(
        3,
        127,
        127,
        127,
        127,
        NULL,
        NULL,
        DATE('0001-01-01'),
        datetime('0001-01-01 11:22:33'),
        NULL,
        NULL,
        NULL,
        127,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
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
        sat_test_dataset.sat_full_dataset
    VALUES(
        4,
        9223372036854775807,
        999999999999999999,
        999999999999999999,
        0.123456789,
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
        999999999999999999,
        999999999999999999
    );

INSERT
    INTO
        sat_test_dataset.sat_full_dataset
    VALUES(
        5,
        - 9223372036854775808,
        - 999999999999999999,
        - 999999999999999999,
        - 0.123456789,
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
        - 999999999999999999,
        - 999999999999999999
    );

INSERT
    INTO
        sat_test_dataset.sat_full_dataset
    VALUES(
        6,
        NULL,
        0.123456789,
        0.123456789,
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
        0.123456789,
        0.123456789
    );

INSERT
    INTO
        sat_test_dataset.sat_full_dataset
    VALUES(
        7,
        NULL,
        - 0.123456789,
        - 0.123456789,
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
        - 0.123456789,
        - 0.123456789
    );
