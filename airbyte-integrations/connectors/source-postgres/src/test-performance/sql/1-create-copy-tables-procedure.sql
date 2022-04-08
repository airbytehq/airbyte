CREATE
    OR replace PROCEDURE copy_table(
        tablecount INT
    ) LANGUAGE plpgsql AS $$ DECLARE v_max_table INT;

v_counter_table INT;

v_tnamee VARCHAR(255);

BEGIN v_max_table := tablecount;

v_counter_table := 1;

while v_counter_table < v_max_table loop EXECUTE format(
    'create table test_%s as (select * from test t)',
    v_counter_table
);

v_counter_table := v_counter_table + 1;
END loop;

COMMIT;
END;

$$
