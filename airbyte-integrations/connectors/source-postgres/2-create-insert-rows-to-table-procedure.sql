create or replace procedure insert_rows(allrows int, insertcount int, value text)
language plpgsql
as $$
declare dummyIpsum varchar(255); fieldText text; vmax int; vmaxx int; vmaxoneinsert int; counter int;
declare lastinsertcounter int; lastinsert int; fullloop int; fullloopcounter int; insertTable text; insertTableLasted text;

begin
	fieldText := value;
	dummyIpsum = '''dummy_ipsum''';
	vmax = allrows;
	vmaxx = allrows;
	vmaxoneinsert = insertcount;
	counter = 1;
	lastinsertcounter = 1;
	lastinsert = 0;
	fullloop = 0;
	fullloopcounter = 0;

	while vmaxx <= vmaxoneinsert loop
      vmaxoneinsert := vmaxx;
	  fullloop := fullloop + 1;
	  vmaxx := vmaxx + 1;
   	end loop;
    commit;

   	while vmax > vmaxoneinsert loop
      fullloop := fullloop + 1;
	  vmax := vmax - vmaxoneinsert;
	 lastinsert := vmax;
   	end loop;
    commit;

   insertTable := 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (';
	while counter < vmaxoneinsert loop
      insertTable := concat(insertTable, dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', fieldText, ', CURRENT_TIMESTAMP), (');
	  counter := counter + 1;
   	end loop;
    commit;
	insertTable := concat(insertTable, dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', fieldText, ', CURRENT_TIMESTAMP);');

	while vmax < 1 loop
      fullloop := 0;
	  vmax := 1;
   	end loop;
    commit;

   while fullloopcounter < fullloop loop
      EXECUTE insertTable;
	  fullloopcounter := fullloopcounter + 1;
   	end loop;
    commit;

   insertTableLasted := 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (';
	while lastinsertcounter < lastinsert loop
      insertTableLasted := concat(insertTableLasted, dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', fieldText, ', CURRENT_TIMESTAMP), (');
      lastinsertcounter := lastinsertcounter + 1;
   	end loop;
    commit;
	insertTableLasted := concat(insertTableLasted, dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', dummyIpsum, ', ', fieldText, ', CURRENT_TIMESTAMP);');

	while lastinsert > 0 loop
      EXECUTE insertTableLasted;
	  lastinsert := 0;
   	end loop;
    commit;
end;$$


