# MsSQL (SQL Server) Source

## Performance Test

### Use MsSQL script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them, 
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in **mssql-script.sql** to change the number of tables, and the number of records of different sizes.
3. Execute the script with your changes for the new database. 
You can run the script use the MySQL command line client: - **mysql -h hostname -u user database < path/to/script/mssql-script.sql**
After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.
