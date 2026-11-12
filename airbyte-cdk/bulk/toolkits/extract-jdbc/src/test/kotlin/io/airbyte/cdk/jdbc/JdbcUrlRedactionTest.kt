/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcUrlRedactionTest {
    @Test
    fun testNetSuiteOauth2TokenAtEndOfCustomProperties() {
        Assertions.assertEquals(
            "jdbc:ns://host.example:1708;ServerDataSource=NetSuite2.com;encrypted=1;NegotiateSSLClose=false;CustomProperties=(AccountID=TSTACCT;RoleID=5;OAuth2Token=****)",
            redactJdbcUrl(
                "jdbc:ns://host.example:1708;ServerDataSource=NetSuite2.com;encrypted=1;NegotiateSSLClose=false;CustomProperties=(AccountID=TSTACCT;RoleID=5;OAuth2Token=fake-oauth2-token-value)",
            ),
        )
    }

    @Test
    fun testNetSuiteOauth2TokenAtStartOfCustomProperties() {
        Assertions.assertEquals(
            "jdbc:ns://host.example:1708;ServerDataSource=NetSuite2.com;encrypted=1;NegotiateSSLClose=false;CustomProperties=(OAuth2Token=****;AccountID=TSTACCT;RoleID=5)",
            redactJdbcUrl(
                "jdbc:ns://host.example:1708;ServerDataSource=NetSuite2.com;encrypted=1;NegotiateSSLClose=false;CustomProperties=(OAuth2Token=fake-oauth2-token-value;AccountID=TSTACCT;RoleID=5)",
            ),
        )
    }

    @Test
    fun testPostgresPasswordParameters() {
        Assertions.assertEquals(
            "jdbc:postgresql://host:5432/db?user=u&password=****&sslmode=require&sslpassword=****",
            redactJdbcUrl(
                "jdbc:postgresql://host:5432/db?user=u&password=p1&sslmode=require&sslpassword=p2",
            ),
        )
    }

    @Test
    fun testSqlServerBracedPassword() {
        Assertions.assertEquals(
            "jdbc:sqlserver://host;password=****;encrypt=true",
            redactJdbcUrl("jdbc:sqlserver://host;password={a;b};encrypt=true"),
        )
    }

    @Test
    fun testUrlUserinfoPassword() {
        Assertions.assertEquals(
            "jdbc:mysql://user:****@host:3306/db",
            redactJdbcUrl("jdbc:mysql://user:p3@host:3306/db"),
        )
    }

    @Test
    fun testMixedCaseCredentialKeys() {
        Assertions.assertEquals(
            "jdbc:test://host;PWD=****&ApiKey=****;Client_Secret=****",
            redactJdbcUrl("jdbc:test://host;PWD=x&ApiKey=y;Client_Secret=z"),
        )
    }

    @Test
    fun testUrlWithoutCredentialsIsUnchanged() {
        val jdbcUrl = "jdbc:sqlserver://h:1433;databaseName=db"
        Assertions.assertEquals(jdbcUrl, redactJdbcUrl(jdbcUrl))
    }
}
