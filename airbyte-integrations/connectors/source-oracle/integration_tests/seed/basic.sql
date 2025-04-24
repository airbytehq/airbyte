CREATE
    USER ORACLE_BASIC IDENTIFIED BY TEST DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON
    USERS;

CREATE
    TABLE
        TEST.TEST_DATASET(
            ID INTEGER PRIMARY KEY,
            TEST_COLUMN_1 CHAR(
                3 CHAR
            ),
            TEST_COLUMN_11 DATE,
            TEST_COLUMN_12 TIMESTAMP,
            TEST_COLUMN_13 TIMESTAMP WITH TIME ZONE,
            TEST_COLUMN_14 TIMESTAMP WITH LOCAL TIME ZONE,
            TEST_COLUMN_2 VARCHAR2(256),
            TEST_COLUMN_3 VARCHAR2(256),
            TEST_COLUMN_4 NVARCHAR2(3),
            TEST_COLUMN_5 NUMBER,
            TEST_COLUMN_6 NUMBER(
                6,
                - 2
            ),
            TEST_COLUMN_7 FLOAT(5),
            TEST_COLUMN_8 FLOAT
        );

INSERT
    INTO
        TEST.TEST_DATASET
    VALUES(
        1,
        'a',
        to_date(
            '-4700/01/01',
            'syyyy/mm/dd'
        ),
        to_timestamp(
            '2020-06-10 06:14:00.742',
            'YYYY-MM-DD HH24:MI:SS.FF'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00 EST',
            'DD-MON-YYYY HH24:MI:SS TZR'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00.000456',
            'DD-MON-YYYY HH24:MI:SS.FF'
        ),
        'тест',
        chr(33)|| chr(34)|| chr(35)|| chr(36)|| chr(37)|| chr(38)|| chr(39)|| chr(40)|| chr(41),
        N'テスト',
        1,
        123.89,
        1.34,
        126.45
    );

INSERT
    INTO
        TEST.TEST_DATASET
    VALUES(
        2,
        'ab',
        to_date(
            '9999/12/31 23:59:59',
            'yyyy/mm/dd hh24:mi:ss'
        ),
        to_timestamp(
            '2020-06-10 06:14:00.742123',
            'YYYY-MM-DD HH24:MI:SS.FF'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00.123456 EST',
            'DD-MON-YYYY HH24:MI:SS.FF TZR'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00.000456',
            'DD-MON-YYYY HH24:MI:SS.FF'
        ),
        '⚡ test ��',
        chr(33)|| chr(34)|| chr(35)|| chr(36)|| chr(37)|| chr(38)|| chr(39)|| chr(40)|| chr(41),
        N'テスト',
        123.45,
        123.89,
        126.45,
        126
    );

INSERT
    INTO
        TEST.TEST_DATASET
    VALUES(
        3,
        'abc',
        to_date(
            '9999/12/31 23:59:59',
            'yyyy/mm/dd hh24:mi:ss'
        ),
        to_timestamp(
            '2020-06-10 06:14:00.742123',
            'YYYY-MM-DD HH24:MI:SS.FF'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00 -5:00',
            'DD-MON-YYYY HH24:MI:SS TZH:TZM'
        ),
        to_timestamp_tz(
            '21-FEB-2009 18:00:00.000456',
            'DD-MON-YYYY HH24:MI:SS.FF'
        ),
        q'[{|}!"#$%&'()*+,
        -./:;

<=>? @ [] ^_ `~] ', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N' テスト', power(10, -130), 123.89, 126.45, 126);
INSERT INTO TEST.TEST_DATASET VALUES (4, ' abc', to_date(' 9999 / 12 / 31 23:59:59 ',' yyyy / mm / dd hh24:mi:ss'), to_timestamp(' 2020 - 06 - 10 06:14:00.742123 ', ' YYYY - MM - DD HH24:MI:SS.FF'), to_timestamp_tz(' 21 - FEB - 2009 18:00:00.123456 - 5:00 ', ' DD - MON - YYYY HH24:MI:SS.FF TZH:TZM'), to_timestamp_tz(' 21 - FEB - 2009 18:00:00.000456 ', ' DD - MON - YYYY HH24:MI:SS.FF'), q' [ { | } ! "#$%&'()*+,-./:;<=>?@[]^_`~]', chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41), N'テスト', 9.99999999999999999999 * power(10, 125), 123.89, 126.45, 126);
INSERT INTO TEST.TEST_DATASET VALUES (5, 'abc', to_date('9999/12/31 23:59:59','yyyy/mm/dd hh24:mi:ss'), to_timestamp('2020-06-10 06:14:00.742123', 'YYYY-MM-DD HH24:MI:SS.FF'), to_timestamp_tz('21-FEB-2009 18:00:00.123456 -5:00', 'DD-MON-YYYY HH24:MI:SS.FF TZH:TZM'), to_timestamp_tz('21-FEB-2009 18:00:00.000456', 'DD-MON-YYYY HH24:MI:SS.FF'), q'[{|}!" #$ %& '()*+,-./:;<=>?@[]^_`~]',
chr(33)|| chr(34)|| chr(35)|| chr(36)|| chr(37)|| chr(38)|| chr(39)|| chr(40)|| chr(41),
N'テスト',
9.99999999999999999999 * POWER( 10, 125 ),
123.89,
126.45,
126
    );
