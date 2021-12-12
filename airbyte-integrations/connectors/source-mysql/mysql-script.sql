delimiter #
create procedure table_copy(in tablecount int)
begin

set @v_max_table = tablecount;
set @v_counter_table = 1;

while @v_counter_table < @v_max_table do
set @tnamee = concat('create table IF NOT EXISTS test_', @v_counter_table, ' SELECT * FROM test;');
PREPARE stmt from @tnamee;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
set @v_counter_table = @v_counter_table + 1;
end while;
commit;

end #

delimiter ;

delimiter #
create procedure insert_rows(in allrows int, in insertcount int, in value longblob)
begin

set @dummyIpsum = '\'dummy_ipsum\'';
set @fieldText = value;
set @vmax = allrows;
set @vmaxx = allrows;
set @vmaxoneinsert = insertcount;
set @counter = 1;
set @lastinsertcounter = 1;
set @lastinsert = 0;
set @fullloop = 0;
set @fullloopcounter = 0;

while @vmaxx <= @vmaxoneinsert do
	set @vmaxoneinsert = @vmaxx;
	set @fullloop = @fullloop + 1;
	set @vmaxx = @vmaxx + 1;
end while;
commit;

while @vmax > @vmaxoneinsert do
	set @fullloop = @fullloop + 1;
	set @vmax = @vmax - @vmaxoneinsert;
	set @lastinsert = @vmax;
end while;
commit;

set @insertTable = concat('insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (');
while @counter < @vmaxoneinsert do
	set @insertTable = concat(@insertTable, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP), (');
	set @counter = @counter + 1;
end while;
commit;
set @insertTable = concat(@insertTable, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP);');

while @vmax < 1 do
	set @fullloop = 0;
	set @vmax = 1;
end while;
commit;

while @fullloopcounter < @fullloop do
	PREPARE runinsert from @insertTable;
	EXECUTE runinsert;
	DEALLOCATE PREPARE runinsert;
	set @fullloopcounter = @fullloopcounter + 1;
end while;
commit;

set @insertTableLasted = concat('insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (');
while @lastinsertcounter < @lastinsert do
	set @insertTableLasted = concat(@insertTableLasted, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP), (');
	set @lastinsertcounter = @lastinsertcounter + 1;
end while;
commit;
set @insertTableLasted = concat(@insertTableLasted, @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @dummyIpsum, ', ', @fieldText, ', CURRENT_TIMESTAMP);');

while @lastinsert > 0 do
	PREPARE runinsert from @insertTableLasted;
	EXECUTE runinsert;
	DEALLOCATE PREPARE runinsert;
	set @lastinsert = 0;
end while;
commit;

end #

delimiter ;

delimiter #
create procedure table_create()
begin

create table test
(
id int unsigned not null auto_increment primary key,
varchar1 varchar(255),
varchar2 varchar(255),
varchar3 varchar(255),
varchar4 varchar(255),
varchar5 varchar(255),
longblobfield longblob,
timestampfield timestamp
)
engine=innodb;

set @extraSmallText = '\'test weight 50b - some text, some text, some text\'';
set @smallText = CONCAT('\'test weight 500b - ', REPEAT('some text, some text, ', 20), '\'');
set @regularText = CONCAT('\'test weight 10kb - ', REPEAT('some text, some text, ', 590), '\'');
set @largeText = CONCAT('\'test weight 100kb - ', REPEAT('some text, some text, ', 4450), '\'');

-- TODO: change the following @allrows to control the number of records with different sizes
-- number of 50B records
call insert_rows(0, 5000000, @extraSmallText);
-- number of 500B records
call insert_rows(0, 50000, @smallText);
-- number of 10KB records
call insert_rows(0, 5000, @regularText);
-- number of 100KB records
call insert_rows(0, 50, @largeText);
end #

delimiter ;

call table_create();
drop procedure if exists table_create;
drop procedure if exists insert_rows;

-- TODO: change the value to control the number of tables
call table_copy(1);
drop procedure if exists table_copy;
ALTER TABLE test RENAME test_0;
