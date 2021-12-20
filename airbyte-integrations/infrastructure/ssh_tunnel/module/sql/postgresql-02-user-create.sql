-- create the specific user we want to use from airbyte
CREATE
    USER testcaseuser WITH password 'ThisIsNotTheRealPassword.PleaseSetThisByHand';

GRANT integrationtest_rw TO testcaseuser;
