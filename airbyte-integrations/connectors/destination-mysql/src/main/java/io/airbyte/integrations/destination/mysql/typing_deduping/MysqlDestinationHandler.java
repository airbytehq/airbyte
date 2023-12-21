package io.airbyte.integrations.destination.mysql.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;

public class MysqlDestinationHandler extends JdbcDestinationHandler {
  public MysqlDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase);
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    // mysql's information_schema.table.table_rows is an approximation.
    // select exists should be reasonably efficient and also gives us the information we need.
    final int rowCount = jdbcDatabase.queryInt(
        DSL.using(SQLDialect.MYSQL).select(
            DSL.case_().when(DSL.exists(DSL.selectOne().from(DSL.name(id.finalNamespace(), id.finalName()))), 1).else_(0)
        ).getSQL(ParamType.INLINED));
    return rowCount == 0;
  }
}
