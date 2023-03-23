CREATE USER ORACLE_FULL_NN IDENTIFIED BY TEST DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS;

CREATE TABLE ORACLE_FULL_NN.TEST_DATASET(ID INTEGER PRIMARY KEY, TEST_COLUMN_1 CHAR(3 CHAR),TEST_COLUMN_10 BINARY_DOUBLE,TEST_COLUMN_11 DATE,TEST_COLUMN_12 TIMESTAMP,TEST_COLUMN_13 TIMESTAMP WITH TIME ZONE,TEST_COLUMN_14 TIMESTAMP WITH LOCAL TIME ZONE,TEST_COLUMN_15 INTERVAL YEAR TO MONTH,TEST_COLUMN_16 BLOB,TEST_COLUMN_17 CLOB,TEST_COLUMN_18 RAW(200),TEST_COLUMN_19 XMLTYPE,TEST_COLUMN_2 VARCHAR2(256),TEST_COLUMN_3 VARCHAR2(256),TEST_COLUMN_4 NVARCHAR2(3),TEST_COLUMN_5 NUMBER,TEST_COLUMN_6 NUMBER(6,-2),TEST_COLUMN_7 FLOAT(5),TEST_COLUMN_8 FLOAT,TEST_COLUMN_9 BINARY_FLOAT );

INSERT INTO ORACLE_FULL_NN.TEST_DATASET VALUES (1, 'a', 126.45d, to_date('-4700/01/01','syyyy/mm/dd'), to_timestamp('2020-06-10 06:14:00.742', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00 EST', 'DD-MON-YYYY HH24:MI:SS TZR'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), INTERVAL '10-2' YEAR TO MONTH, utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), xmltype('<?xml version="1.0" encoding="UTF-8"?>
<list_configuration>
<config>1</config>
<config>2</config>
</list_configuration>'), 'тест', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', 1, 123.89, 1.34, 126.45, 126.45f);
INSERT INTO ORACLE_FULL_NN.TEST_DATASET VALUES (2, 'ab', 2.22507485850720E-308, to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss'), to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00.123456 EST', 'DD-MON-YYYY HH24:MI:SS.FF TZR'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), INTERVAL '9' MONTH, utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), xmltype('<?xml version="1.0" encoding="UTF-8"?>
<list_configuration>
<config>1</config>
<config>2</config>
</list_configuration>'), '⚡ test ��', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', 123.45, 123.89, 126.45, 126, 1.17549E-38f);
INSERT INTO ORACLE_FULL_NN.TEST_DATASET VALUES (3, 'abc', 1.79769313486231E+308d, to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss'), to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00 -5:00', 'DD-MON-YYYY HH24:MI:SS TZH:TZM'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), INTERVAL '9' MONTH, utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), xmltype('<?xml version="1.0" encoding="UTF-8"?>
<list_configuration>
<config>1</config>
<config>2</config>
</list_configuration>'), q'[{|}!"#$%&'()*+,-./:;<=>?@[]^_`~]', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', power(10, -130), 123.89, 126.45, 126, 3.40282347E+038f);
INSERT INTO ORACLE_FULL_NN.TEST_DATASET VALUES (4, 'abc', BINARY_DOUBLE_INFINITY, to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss'), to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00.123456 -5:00', 'DD-MON-YYYY HH24:MI:SS.FF TZH:TZM'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), INTERVAL '9' MONTH, utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), xmltype('<?xml version="1.0" encoding="UTF-8"?>
<list_configuration>
<config>1</config>
<config>2</config>
</list_configuration>'), q'[{|}!"#$%&'()*+,-./:;<=>?@[]^_`~]', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', 9.99999999999999999999 * power(10, 125), 123.89, 126.45, 126, BINARY_FLOAT_INFINITY);
INSERT INTO ORACLE_FULL_NN.TEST_DATASET VALUES (5, 'abc', BINARY_DOUBLE_INFINITY, to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss'), to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00.123456 -5:00', 'DD-MON-YYYY HH24:MI:SS.FF TZH:TZM'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), INTERVAL '9' MONTH, utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), utl_raw.cast_to_raw('some content here'), xmltype('<?xml version="1.0" encoding="UTF-8"?>
<list_configuration>
<config>1</config>
<config>2</config>
</list_configuration>'), q'[{|}!"#$%&'()*+,-./:;<=>?@[]^_`~]', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', 9.99999999999999999999 * power(10, 125), 123.89, 126.45, 126, BINARY_FLOAT_INFINITY);
