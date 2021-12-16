CREATE
    OR replace PROCEDURE insert_rows(
        allrows INT,
        insertcount INT,
        value text
    ) LANGUAGE plpgsql AS $$ DECLARE dummyIpsum VARCHAR(255);

fieldText text;

vmax INT;

vmaxx INT;

vmaxoneinsert INT;

counter INT;

DECLARE lastinsertcounter INT;

lastinsert INT;

fullloop INT;

fullloopcounter INT;

insertTable text;

insertTableLasted text;

BEGIN fieldText := value;

dummyIpsum = '''dummy_ipsum''';

vmax = allrows;

vmaxx = allrows;

vmaxoneinsert = insertcount;

counter = 1;

lastinsertcounter = 1;

lastinsert = 0;

fullloop = 0;

fullloopcounter = 0;

while vmaxx <= vmaxoneinsert loop vmaxoneinsert := vmaxx;

fullloop := fullloop + 1;

vmaxx := vmaxx + 1;
END loop;

COMMIT;

while vmax > vmaxoneinsert loop fullloop := fullloop + 1;

vmax := vmax - vmaxoneinsert;

lastinsert := vmax;
END loop;

COMMIT;

insertTable := 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (';

while counter < vmaxoneinsert loop insertTable := concat(
    insertTable,
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    fieldText,
    ', CURRENT_TIMESTAMP), ('
);

counter := counter + 1;
END loop;

COMMIT;

insertTable := concat(
    insertTable,
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    fieldText,
    ', CURRENT_TIMESTAMP);'
);

while vmax < 1 loop fullloop := 0;

vmax := 1;
END loop;

COMMIT;

while fullloopcounter < fullloop loop EXECUTE insertTable;

fullloopcounter := fullloopcounter + 1;
END loop;

COMMIT;

insertTableLasted := 'insert into test (varchar1, varchar2, varchar3, varchar4, varchar5, longblobfield, timestampfield) values (';

while lastinsertcounter < lastinsert loop insertTableLasted := concat(
    insertTableLasted,
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    fieldText,
    ', CURRENT_TIMESTAMP), ('
);

lastinsertcounter := lastinsertcounter + 1;
END loop;

COMMIT;

insertTableLasted := concat(
    insertTableLasted,
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    dummyIpsum,
    ', ',
    fieldText,
    ', CURRENT_TIMESTAMP);'
);

while lastinsert > 0 loop EXECUTE insertTableLasted;

lastinsert := 0;
END loop;

COMMIT;
END;

$$
