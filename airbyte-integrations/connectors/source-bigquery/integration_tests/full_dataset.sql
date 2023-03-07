CREATE TABLE
    sat_test_dataset.sat_full_dataset(id NUMERIC(29),
                                      test_column_1 int64,
                                      test_column_10 decimal(29,
                                             9),
                                      test_column_11 bigdecimal(76,
                                          38),
                                      test_column_12 float64,
                                      test_column_13 bool,
                                      test_column_14 bytes,
                                      test_column_15 date,
                                      test_column_16 datetime,
                                      test_column_17 timestamp,
                                      test_column_18 geography,
                                      test_column_19 string,
                                      test_column_2 int,
                                      test_column_20 STRUCT<course STRING,
                                      id INT64>,
                                      test_column_21 time,
                                      test_column_22 ARRAY<String>,
                                      test_column_23 STRUCT<frst String,
                                      sec int64,
                                      obbj STRUCT<id_col int64,
                                      mega_obbj STRUCT<last_col time>>>,
                                      test_column_24 ARRAY<STRUCT<fff String,
                                      ggg int64>>,
                                      test_column_25 ARRAY<STRUCT<fff String,
                                      ggg ARRAY<STRUCT<ooo String,
                                      kkk int64>>>>,
                                      test_column_26 INTERVAL,
                                      test_column_3 smallint,
                                      test_column_4 integer,
                                      test_column_5 bigint,
                                      test_column_6 tinyint,
                                      test_column_7 byteint,
                                      test_column_8 numeric(29,
                                             9),
                                      test_column_9 bignumeric(76,
                                          38) );

INSERT INTO sat_test_dataset.sat_full_dataset VALUES (1, null, null, null, null, true, FROM_BASE64("test"), date('2021-10-20'), datetime('2021-10-20 11:22:33'), timestamp('2021-10-20 11:22:33'), ST_GEOGFROMTEXT('POINT(1 2)'), 'qwe', null, STRUCT("B.A",12), TIME(15, 30, 00), ['a', 'b'], STRUCT('s' as frst, 1 as sec, STRUCT(555 as id_col, STRUCT(TIME(15, 30, 00) as time) as mega_obbj) as obbj), [STRUCT('qqq' as fff, 1 as ggg), STRUCT('kkk' as fff, 2 as ggg)], [STRUCT('qqq' as fff, [STRUCT('fff' as ooo, 1 as kkk), STRUCT('hhh' as ooo, 2 as kkk)] as ggg)], MAKE_INTERVAL(2021, 10, 10, 10, 10, 10), null, null, null, null, null, null, null);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (2, -128, -128, -128, -128, false, null, date('9999-12-31'), datetime('9999-12-31 11:22:33'), null, null, 'йцу', -128, null, null, null, null, null, null, null, -128, -128, -128, -128, -128, -128, -128);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (3, 127, 127, 127, 127, null, null, date('0001-01-01'), datetime('0001-01-01 11:22:33'), null, null, null, 127, null, null, null, null, null, null, null, 127, 127, 127, 127, 127, 127, 127);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (4, 9223372036854775807, 999999999999999999, 999999999999999999, 0.123456789, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 999999999999999999, 999999999999999999);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (5, -9223372036854775808, -999999999999999999, -999999999999999999, -0.123456789, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, -999999999999999999, -999999999999999999);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (6, null, 0.123456789, 0.123456789, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 0.123456789, 0.123456789);
INSERT INTO sat_test_dataset.sat_full_dataset VALUES (7, null, -0.123456789, -0.123456789, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, -0.123456789, -0.123456789);
