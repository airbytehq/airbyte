create sequence test_seq;

create table test(
id int check (id > 0) not null default nextval ('test_seq') primary key,
varchar1 varchar(255),
varchar2 varchar(255),
varchar3 varchar(255),
varchar4 varchar(255),
varchar5 varchar(255),
longblobfield bytea,
timestampfield timestamp(0));

-- TODO: change the following @allrows to control the number of records with different sizes
-- number of 50B records
call insert_rows(0, 500000, '''test weight 50b - some text, some text, some text''');
-- number of 500B records
call insert_rows(0, 50000, CONCAT('''test weight 500b - ', repeat('some text, some text, ', 20), 'some text'''));
-- number of 10KB records
call insert_rows(0, 5000, CONCAT('''test weight 10kb - ', repeat('some text, some text, some text, some text, ', 295), 'some text'''));
-- number of 100KB records
call insert_rows(0, 50, CONCAT('''test weight 100kb - ', repeat('some text, some text, ', 4450), 'some text'''));
-- TODO: change the value to control the number of tables
call copy_table(0);
ALTER TABLE test RENAME TO test_0;


