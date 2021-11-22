package io.airbyte.integrations.source.cockroachdb;

import org.junit.jupiter.api.Test;
import org.postgresql.ds.PGSimpleDataSource;

import java.sql.Connection;

public class ttt {

    @Test
    public void sss() throws Exception {
        PGSimpleDataSource ds = new PGSimpleDataSource();

        ds.setServerNames(new String[]{"localhost"});
        ds.setPortNumbers(new int[]{26257});
        ds.setDatabaseName("defaultdb");
        ds.setUser("test_user");
        ds.setPassword("test_user");
        ds.setSsl(true);
        ds.setSslMode("require");
        ds.setApplicationName("CockroachDbJdbcEncryptSourceAcceptanceTest");

        System.out.println(ds.getProtocolVersion());
        System.out.println(ds.getSslHostnameVerifier());
        System.out.println(ds.getSslCert());

        Connection connection = ds.getConnection();
        System.out.println(connection.prepareCall("select 1").execute());
    }
}
