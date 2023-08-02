delimiter # CREATE
    PROCEDURE table_copy(
        IN tablecount INT
    ) BEGIN
SET
    @v_max_table = tablecount;
SET
@v_counter_table = 1;

while @v_counter_table < @v_max_table do
SET
@tnamee = concat(
    'create table IF NOT EXISTS test_',
    @v_counter_table,
    ' SELECT * FROM test;'
);

PREPARE stmt
FROM
@tnamee;

EXECUTE stmt;

DEALLOCATE PREPARE stmt;
SET
@v_counter_table = @v_counter_table + 1;
END while;

COMMIT;
END # delimiter;

delimiter # CREATE
    PROCEDURE insert_rows(
        IN allrows INT,
        IN insertcount INT,
        IN value longblob
    ) BEGIN
SET
    @dummyIpsum = '\' dummy_ipsum\'';
SET
@fieldText = value;
SET
@vmax = allrows;
SET
@vmaxx = allrows;
SET
@vmaxoneinsert = insertcount;
SET
@counter = 1;
SET
@lastinsertcounter = 1;
SET
@lastinsert = 0;
SET
@fullloop = 0;
SET
@fullloopcounter = 0;

while @vmaxx <= @vmaxoneinsert do
SET
@vmaxoneinsert = @vmaxx;
SET
@fullloop = @fullloop + 1;
SET
@vmaxx = @vmaxx + 1;
END while;

COMMIT;

while @vmax > @vmaxoneinsert do
SET
@fullloop = @fullloop + 1;
SET
@vmax = @vmax - @vmaxoneinsert;
SET
@lastinsert = @vmax;
END while;

COMMIT;
SET
@insertTable = concat('insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longtextfield, timestampfield) values (');

while @counter < @vmaxoneinsert do
SET
@insertTable = concat(
    @insertTable,
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @fieldText,
    ', CURRENT_TIMESTAMP), ('
);
SET
@counter = @counter + 1;
END while;

COMMIT;
SET
@insertTable = concat(
    @insertTable,
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @fieldText,
    ', CURRENT_TIMESTAMP);'
);

while @vmax < 1 do
SET
@fullloop = 0;
SET
@vmax = 1;
END while;

COMMIT;

while @fullloopcounter < @fullloop do PREPARE runinsert
FROM
@insertTable;

EXECUTE runinsert;

DEALLOCATE PREPARE runinsert;
SET
@fullloopcounter = @fullloopcounter + 1;
END while;

COMMIT;
SET
@insertTableLasted = concat('insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longtextfield, timestampfield) values (');

while @lastinsertcounter < @lastinsert do
SET
@insertTableLasted = concat(
    @insertTableLasted,
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @fieldText,
    ', CURRENT_TIMESTAMP), ('
);
SET
@lastinsertcounter = @lastinsertcounter + 1;
END while;

COMMIT;
SET
@insertTableLasted = concat(
    @insertTableLasted,
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @dummyIpsum,
    ', ',
    @fieldText,
    ', CURRENT_TIMESTAMP);'
);

while @lastinsert > 0 do PREPARE runinsert
FROM
@insertTableLasted;

EXECUTE runinsert;

DEALLOCATE PREPARE runinsert;
SET
@lastinsert = 0;
END while;

COMMIT;
END # delimiter;

delimiter # CREATE
    PROCEDURE table_create() BEGIN CREATE
        TABLE
            test(
                id INT unsigned NOT NULL auto_increment PRIMARY KEY,
                varchar1 VARCHAR(255),
                varchar2 VARCHAR(255),
                varchar3 VARCHAR(255),
                varchar4 VARCHAR(255),
                varchar5 VARCHAR(255),
                longtextfield longtext,
                timestampfield TIMESTAMP
            ) engine = innodb;
SET
@extraSmallText = '\' test weight 50 b - SOME text,
SOME text,
SOME text\'';
SET
@smallText = CONCAT(
    '\' test weight 500 b - ', REPEAT(' SOME text,
    SOME text,
    ', 20), ' \''
);
SET
@regularText = CONCAT(
    '\' test weight 10 kb - ', REPEAT(' SOME text,
    SOME text,
    ', 590), ' \''
);
SET
@largeText = CONCAT(
    '\' test weight 100 kb - ', REPEAT(' SOME text,
    SOME text,
    ', 4450), ' \''
);

-- TODO: change the following @allrows to control the number of records with different sizes
-- number of 50B records
CALL insert_rows(
    0,
    5000000,
    @extraSmallText
);

-- number of 500B records
CALL insert_rows(
    0,
    50000,
    @smallText
);

-- number of 10KB records
CALL insert_rows(
    0,
    5000,
    @regularText
);

-- number of 100KB records
CALL insert_rows(
    0,
    50,
    @largeText
);
END # delimiter;

CALL table_create();

DROP
    PROCEDURE IF EXISTS table_create;

DROP
    PROCEDURE IF EXISTS insert_rows;

-- TODO: change the value to control the number of tables
CALL table_copy(1);

DROP
    PROCEDURE IF EXISTS table_copy;

ALTER TABLE
    test RENAME test_0;