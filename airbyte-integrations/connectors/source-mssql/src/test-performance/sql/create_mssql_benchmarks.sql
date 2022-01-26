CREATE
    PROCEDURE table_copy(
        @tablecount INT
    ) AS BEGIN
SET
    nocount ON;
    
    DECLARE @v_max_table INT;

DECLARE @v_counter_table INT;

DECLARE @tnamee VARCHAR(255);
SET
@v_max_table = @tablecount;
SET
@v_counter_table = 1;

while @v_counter_table < @v_max_table BEGIN
SET
@tnamee = concat(
    'SELECT * INTO test_',
    @v_counter_table,
    ' FROM test;'
);

EXEC(@tnamee);
SET
@v_counter_table = @v_counter_table + 1;
END;
END;

GO --
CREATE
    PROCEDURE insert_rows(
        @allrows INT,
        @insertcount INT,
        @value NVARCHAR(MAX)
    ) AS BEGIN
SET
    nocount ON;
    
    DECLARE @dummyIpsum VARCHAR(255) DECLARE @fieldText NVARCHAR(MAX)
SET
    @fieldText = @value DECLARE @vmax INT;

DECLARE @vmaxx INT;

DECLARE @vmaxoneinsert INT;

DECLARE @counter INT;

DECLARE @lastinsertcounter INT;

DECLARE @lastinsert INT;

DECLARE @fullloop INT;

DECLARE @fullloopcounter INT;
SET
@vmax = @allrows;
SET
@vmaxx = @allrows;
SET
@vmaxoneinsert = @insertcount;
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
SET
@dummyIpsum = '''dummy_ipsum''' while @vmaxx <= @vmaxoneinsert BEGIN
SET
@vmaxoneinsert = @vmaxx;
SET
@fullloop = @fullloop + 1;
SET
@vmaxx = @vmaxx + 1;
END;

while @vmax > @vmaxoneinsert BEGIN
SET
@fullloop = @fullloop + 1;
SET
@vmax = @vmax - @vmaxoneinsert;
SET
@lastinsert = @vmax;
END;

DECLARE @insertTable NVARCHAR(MAX)
SET
@insertTable = CONVERT(
    NVARCHAR(MAX),
    'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longtextfield, timestampfield) values ('
);

while @counter < @vmaxoneinsert BEGIN
SET
@insertTable = CONVERT(
    NVARCHAR(MAX),
    concat(
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
    )
);
SET
@counter = @counter + 1;
END;
SET
@insertTable = CONVERT(
    NVARCHAR(MAX),
    concat(
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
    )
);

while @vmax < 1 BEGIN
SET
@fullloop = 0
SET
@vmax = 1
END;

while @fullloopcounter < @fullloop BEGIN EXEC(@insertTable);
SET
@fullloopcounter = @fullloopcounter + 1;
END;

DECLARE @insertTableLasted NVARCHAR(MAX);
SET
@insertTableLasted = CONVERT(
    NVARCHAR(MAX),
    'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longtextfield, timestampfield) values ('
);

while @lastinsertcounter < @lastinsert BEGIN
SET
@insertTableLasted = CONVERT(
    NVARCHAR(MAX),
    concat(
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
    )
);
SET
@lastinsertcounter = @lastinsertcounter + 1;
END;
SET
@insertTableLasted = CONVERT(
    NVARCHAR(MAX),
    concat(
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
    )
);

while @lastinsert > 0 BEGIN EXEC(@insertTableLasted);
SET
@lastinsert = 0;
END;
END;

GO --
CREATE
    PROCEDURE table_create(
        @val INT
    ) AS BEGIN
SET
    nocount ON;
    
    -- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE
        TABLE
            test(
                id INT CHECK(
                    id > 0
                ) NOT NULL IDENTITY PRIMARY KEY,
                varchar1 VARCHAR(255),
                varchar2 VARCHAR(255),
                varchar3 VARCHAR(255),
                varchar4 VARCHAR(255),
                varchar5 VARCHAR(255),
                longtextfield nvarchar(MAX),
                timestampfield datetime2(0)
            );

DECLARE @extraSmallText NVARCHAR(MAX);

DECLARE @smallText NVARCHAR(MAX);

DECLARE @regularText NVARCHAR(MAX);

DECLARE @largeText NVARCHAR(MAX);

DECLARE @someText nvarchar(MAX);

SELECT
    @someText = N'some text, some text, ';
SET
@extraSmallText = N'''test weight 50b - some text, some text, some text''';
SET
@smallText = N'''test weight 500b - ';
SET
@regularText = N'''test weight 10kb - ';
SET
@largeText = N'''test weight 100kb - ';

SELECT
    @smallText = @smallText + REPLICATE(
        @someText,
        20
    )+ N'''';

SELECT
    @regularText = @regularText + REPLICATE(
        @someText,
        590
    )+ N'some text''';

SELECT
    @largeText = @largeText + REPLICATE(
        @someText,
        4450
    )+ N'some text''';

) -- TODO: change the following @allrows to control the number of records with different sizes
-- number of 50B records
EXEC insert_rows @allrows = 0,
@insertcount = 998,
@value = @extraSmallText -- number of 500B records
EXEC insert_rows @allrows = 0,
@insertcount = 998,
@value = @smallText -- number of 10Kb records
EXEC insert_rows @allrows = 0,
@insertcount = 998,
@value = @regularText -- number of 100Kb records
EXEC insert_rows @allrows = 0,
@insertcount = 98,
@value = @largeText
END;

GO --
EXEC table_create @val = 0 DROP
    PROCEDURE IF EXISTS insert_rows;

DROP
    PROCEDURE IF EXISTS table_create;

-- TODO: change the value to control the number of tables
EXEC table_copy @tablecount = 1;

DROP
    PROCEDURE IF EXISTS table_copy;

EXEC sp_rename 'test',
'test_0';