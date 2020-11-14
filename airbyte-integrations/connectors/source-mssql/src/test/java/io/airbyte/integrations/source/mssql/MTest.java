package io.airbyte.integrations.source.mssql;

import static java.lang.Thread.sleep;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.sql.SQLException;
import java.util.concurrent.TimeUnit;
import org.apache.commons.dbcp2.BasicDataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;
// exec into mssql container (not the test one)
// /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
//
public class MTest {
  @Test
  void test() throws InterruptedException, SQLException {
    final MSSQLServerContainer<?> db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
//        .withInitScript("init.sql");
//        .withUsername("root")
//        .withPassword("");
    db.start();

    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
    System.out.println("dbName = " + dbName);
    System.out.println("db.getJdbcUrl() = " + db.getJdbcUrl());
    System.out.println("db.getFirstMappedPort() = " + db.getFirstMappedPort());

//    database.query(ctx -> ctx.fetch(String.format("SELECT * FROM INFORMATION_SCHEMA.TABLES;")));
    final Database database = getDatabase(db);
    database.query(ctx -> {
      ctx.fetch(String.format("SELECT * FROM INFORMATION_SCHEMA.TABLES;"));
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      return null;
    });

    sleep(TimeUnit.DAYS.toMillis(1));
  }

  public static Database getDatabase(MSSQLServerContainer<?> db) {
    return Databases.createDatabase(
        db.getUsername(),
        db.getPassword(),
        String.format("jdbc:sqlserver://%s:%s",
            db.getHost(),
            db.getFirstMappedPort()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null
        );
  }

}
