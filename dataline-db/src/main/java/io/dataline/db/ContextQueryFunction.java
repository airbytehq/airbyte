package io.dataline.db;

import java.sql.SQLException;
import org.jooq.DSLContext;

@FunctionalInterface
public interface ContextQueryFunction<T> {
  T apply(DSLContext context) throws SQLException;
}
