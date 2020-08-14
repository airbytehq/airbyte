package io.dataline.db;

import static org.jooq.impl.DSL.field;

import java.sql.SQLException;
import java.util.Optional;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.jooq.Result;

/*
The server UUID identifies a specific database installation of Dataline for analytics purposes.
 */
public class ServerUuid {
  public static Optional<String> get(BasicDataSource connectionPool) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        ctx -> {
          Result<Record> result =
              ctx.select().from("dataline_metadata").where(field("key").eq("server-uuid")).fetch();
          Optional<Record> first = result.stream().findFirst();

          if (first.isEmpty()) {
            return Optional.empty();
          } else {
            return Optional.of((String) first.get().get("value"));
          }
        });
  }
}
