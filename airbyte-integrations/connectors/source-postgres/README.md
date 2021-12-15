# Postgres Source

## Performance Test

### Use Postgres script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them, 
you need to follow a few simple steps.

1. Create a new database.
2. On the new database, run script **1-create-copy-tables-procedure.sql** to create the table copy procedure.
   You can run the script use the Postgres command line client: - **psql -h host -d userstoreis -U admin -p port -a -q -f /path/to/script/1-create-copy-tables-procedure.sql**
3. Run script **2-create-insert-rows-to-table-procedure.sql** to create a procedure for creating a table with the specified number of records.
4. Follow the TODOs in **3-run-script.sql** to change the number of tables, and the number of records of different sizes.
5. Execute the **3-run-script.sql** script with your changes for the new database. After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.


