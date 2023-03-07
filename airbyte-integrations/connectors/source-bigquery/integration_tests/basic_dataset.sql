CREATE TABLE
    `sat_test_dataset.sat_basic_dataset`(id NUMERIC(29),
                                         test_column_1 int64,
                                         test_column_10 decimal(29,
                                                9),
                                         test_column_11 bigdecimal(76,
                                             38),
                                         test_column_12 float64,
                                         test_column_13 bool,
                                         test_column_15 date,
                                         test_column_16 datetime,
                                         test_column_17 timestamp,
                                         test_column_19 string,
                                         test_column_2 int,
                                         test_column_21 time,
                                         test_column_3 smallint,
                                         test_column_4 integer,
                                         test_column_5 bigint,
                                         test_column_6 tinyint,
                                         test_column_7 byteint,
                                         test_column_8 numeric(29,
                                                9),
                                         test_column_9 bignumeric(76,
                                             38) );


INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (1, -128, -128, -128, -128, true, date('2021-10-20'), datetime('2021-10-20 11:22:33'), timestamp('2021-10-20 11:22:33'), 'qwe', -128, TIME(15, 30, 00), -128, -128, -128, -128, -128, -128, -128);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (2, 127, 127, 127, 127, false, date('9999-12-31'), datetime('9999-12-31 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, 127, 127);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (3, 9223372036854775807, 999999999999999999, 999999999999999999, 0.123456789, false, date('0001-01-01'), datetime('0001-01-01 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, 999999999999999999, 999999999999999999);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (4, -9223372036854775808, -999999999999999999, -999999999999999999, -0.123456789, false, date('0001-01-01'), datetime('0001-01-01 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, -999999999999999999, -999999999999999999);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (5, -9223372036854775808, 0.123456789, 0.123456789, -0.123456789, false, date('0001-01-01'), datetime('0001-01-01 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, 0.123456789, 0.123456789);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (6, -9223372036854775808, -0.123456789, -0.123456789, -0.123456789, false, date('0001-01-01'), datetime('0001-01-01 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, -0.123456789, -0.123456789);
INSERT INTO sat_test_dataset.sat_basic_dataset VALUES (7, -9223372036854775808, -0.123456789, -0.123456789, -0.123456789, false, date('0001-01-01'), datetime('0001-01-01 11:22:33'), timestamp('2021-10-20 11:22:33'), 'йцу', 127, TIME(15, 30, 00), 127, 127, 127, 127, 127, -0.123456789, -0.123456789);
