create procedure table_copy(@tablecount int)
as
begin
set nocount on;

DECLARE @v_max_table int;
DECLARE @v_counter_table int;
DECLARE @tnamee VARCHAR(255);
set @v_max_table = @tablecount;
set @v_counter_table = 1;

while @v_counter_table < @v_max_table begin
set @tnamee = concat('SELECT * INTO test_', @v_counter_table, ' FROM test;');
EXEC (@tnamee);
set @v_counter_table = @v_counter_table + 1;
end;

end;
go --

create procedure insert_rows( @allrows int, @insertcount int, @value NVARCHAR(max))
as
begin
set nocount on;

DECLARE @dummyIpsum varchar(255)
DECLARE @fieldText NVARCHAR(max)
set @fieldText = @value
DECLARE @vmax int;
DECLARE @vmaxx int;
DECLARE @vmaxoneinsert int;
DECLARE @counter int;
DECLARE @lastinsertcounter int;
DECLARE @lastinsert int;
DECLARE @fullloop int;
DECLARE @fullloopcounter int;
set @dummyIpsum = '''dummy_ipsum'''
set @vmax = @allrows;
set @vmaxx = @allrows;
set @vmaxoneinsert = @insertcount;
set @counter = 1;
set @lastinsertcounter = 1;
set @lastinsert = 0;
set @fullloop = 0;
set @fullloopcounter = 0;

while @vmaxx <= @vmaxoneinsert begin
	set @vmaxoneinsert = @vmaxx;
	set @fullloop = @fullloop + 1;
	set @vmaxx = @vmaxx + 1;
end;

while @vmax > @vmaxoneinsert begin
	set @fullloop = @fullloop + 1;
	set @vmax = @vmax - @vmaxoneinsert;
	set @lastinsert = @vmax;
end;

DECLARE @insertTable NVARCHAR(MAX)
set @insertTable = CONVERT(NVARCHAR(max), 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (');
while @counter < @vmaxoneinsert begin
	set @insertTable = CONVERT(NVARCHAR(max), concat(@insertTable, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP), ('));
	set @counter = @counter + 1;
end;
set @insertTable = CONVERT(NVARCHAR(max), concat(@insertTable, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP);'));

while @vmax < 1 begin
	set @fullloop = 0
	set @vmax = 1
end;

while @fullloopcounter < @fullloop begin
	EXEC (@insertTable);
	set @fullloopcounter = @fullloopcounter + 1;
end;

DECLARE @insertTableLasted NVARCHAR(max);
set @insertTableLasted = CONVERT(NVARCHAR(max), 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (');
while @lastinsertcounter < @lastinsert begin
	set @insertTableLasted = CONVERT(NVARCHAR(max), concat(@insertTableLasted, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP), ('));
	set @lastinsertcounter = @lastinsertcounter + 1;
end;

set @insertTableLasted = CONVERT(NVARCHAR(max), concat(@insertTableLasted, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP);'));

while @lastinsert > 0 begin
	EXEC (@insertTableLasted);
	set @lastinsert = 0;
end;

end;
go --

create procedure table_create(@val int)
as
begin
set nocount on;

-- SQLINES LICENSE FOR EVALUATION USE ONLY
create table test
(
id int check (id > 0) not null identity primary key,
varchar1 varchar(255),
varchar2 varchar(255),
varchar3 varchar(255),
varchar4 varchar(255),
varchar5 varchar(255),
longblobfield nvarchar(max),
timestampfield datetime2(0)
);

DECLARE @extraSmallText NVARCHAR(max);
DECLARE @smallText NVARCHAR(max);
DECLARE @regularText NVARCHAR(max);
DECLARE @largeText NVARCHAR(max);
set @extraSmallText = '''test weight 50b - 50b text, 50b text, 50b text'''
set @smallText = CONCAT('''test weight 500b - ', REPLICATE('some text, some text, ', 20), '''')
set @regularText = CONCAT('''test weight 10kb - ', REPLICATE('some text, some text, some text, some text, ', 295), 'some text''')
set @largeText = CONCAT('''test weight 100kb - ', REPLICATE('some text, some text, some text, some text, ', 2225), 'some text''')
-- TODO: change the following @allrows to control the number of records with different sizes
-- number of 50B records
EXEC insert_rows @allrows = 0, @insertcount = 998, @value = @extraSmallText
-- number of 500B records
EXEC insert_rows @allrows = 0, @insertcount = 998, @value = @smallText
-- number of 10KB records
EXEC insert_rows @allrows = 0, @insertcount = 998, @value = @regularText
-- number of 100KB records
EXEC insert_rows @allrows = 0, @insertcount = 98, @value = @largeText
end;
go --

EXEC table_create @val = 0
drop procedure if exists insert_rows;
drop procedure if exists table_create;

-- TODO: change the value to control the number of tables
EXEC table_copy @tablecount = 1;
drop procedure if exists table_copy;
exec sp_rename 'test', 'test_0';
