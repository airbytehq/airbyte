# MsSQL (SQL Server) Source

## Performance Test

### Running performance tests with CPU and Memory limits for the container

In order to run performance tests with CPU and Memory limits, you need to run the performance test start command with
additional parameters **cpulimit=cpulimit/YOU_CPU_LIMIT** and **memorylimit=memorylimit/YOU_MEMORY_LIMIT**.
**YOU_MEMORY_LIMIT** - RAM limit. Be sure to indicate the limit in MB or GB at the end. Minimum size - 6MB.
**YOU_CPU_LIMIT** - CPU limit. Minimum size - 2.
These parameters are optional and can be used separately from each other.
For example, if you use only **memorylimit=memorylimit/2GB**, only the memory limit for the container will be set, the CPU will not be limited.
Also, if you do not use both of these parameters, then performance tests will run without memory and CPU limitations.


### Use MsSQL script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them, 
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in **mssql-script.sql** to change the number of tables, and the number of records of different sizes.
3. Execute the script with your changes for the new database. 
You can run the script use the MySQL command line client: - **mysql -h hostname -u user database < path/to/script/mssql-script.sql**
After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.
