-- create the specific user we want to use from airbyte
 CREATE
    USER testcaseuser WITH password 'ThisIsNotTheRealPassword.PleaseSetThisByHand';

GRANT CONNECT ON
DATABASE test TO testcaseuser;

GRANT USAGE ON
SCHEMA public TO testcaseuser;

GRANT integrationtest_rw TO testcaseuser;

-- picking a default schema means it can log in without a schema named to connect to, helping test case setup.
ALTER ROLE testcaseuser SET search_path TO public;

