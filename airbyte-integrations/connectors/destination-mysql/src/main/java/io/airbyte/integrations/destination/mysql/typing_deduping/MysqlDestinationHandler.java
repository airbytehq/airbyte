package io.airbyte.integrations.destination.mysql.typing_deduping;

import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.exists;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.selectOne;
import static org.jooq.impl.DSL.using;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;

public class MysqlDestinationHandler extends JdbcDestinationHandler {
  public MysqlDestinationHandler(final String databaseName, final JdbcDatabase jdbcDatabase) {
    super(databaseName, jdbcDatabase);
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    // mysql's information_schema.table.table_rows is an approximation.
    // select exists should be reasonably efficient and also gives us the information we need.
    final int rowCount = jdbcDatabase.queryInt(
        using(SQLDialect.MYSQL).select(
            case_().when(
                exists(selectOne().from(name(id.finalNamespace(), id.finalName()))),
                1
            ).else_(0)
        ).getSQL(ParamType.INLINED));
    return rowCount == 0;
  }
}
