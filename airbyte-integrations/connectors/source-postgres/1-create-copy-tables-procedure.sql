create or replace procedure copy_table(tablecount int)
language plpgsql
as $$
declare v_max_table int; v_counter_table int; v_tnamee VARCHAR(255);
begin
	v_max_table := tablecount;
	v_counter_table := 1;
    while v_counter_table < v_max_table loop
      EXECUTE format('create table test_%s as (select * from test t)', v_counter_table);
	  v_counter_table := v_counter_table + 1;
   end loop;
    commit;
end;$$

