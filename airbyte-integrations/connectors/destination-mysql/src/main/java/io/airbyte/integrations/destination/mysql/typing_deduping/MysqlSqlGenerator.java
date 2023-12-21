package io.airbyte.integrations.destination.mysql.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.apache.commons.lang3.NotImplementedException;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class MysqlSqlGenerator extends JdbcSqlGenerator {
  public MysqlSqlGenerator(final NamingConventionTransformer namingResolver) {
    super(namingResolver);
  }

  private DataType<?> getJsonType() {
    return new DefaultDataType<>(null, String.class, "json");
  }

  @Override
  protected DataType<?> getStructType() {
    return getJsonType();
  }

  @Override
  protected DataType<?> getArrayType() {
    return getJsonType();
  }

  @Override
  public DataType<?> toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      // jooq's TIMESTMAPWITHTIMEZONE type renders to `timestamp with timezone`...
      // which isn't valid mysql syntax.
      // Legacy normalization used char(1024) https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-normalization/dbt-project-template/macros/cross_db_utils/datatypes.sql#L233-L234
      // so match that behavior I guess.
      case TIMESTAMP_WITH_TIMEZONE -> SQLDataType.VARCHAR(1024);
      // Mysql doesn't have a native time with timezone type.
      // Legacy normalization used char(1024) https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/bases/base-normalization/dbt-project-template/macros/cross_db_utils/datatypes.sql#L233-L234
      // so match that behavior I guess.
      case TIME_WITH_TIMEZONE -> SQLDataType.VARCHAR(1024);
      // Mysql VARCHAR can only go up to 16KiB. CLOB translates to mysql TEXT,
      // which supports longer strings.
      case STRING -> SQLDataType.CLOB;
      default -> super.toDialectType(airbyteProtocolType);
    };
  }

  @Override
  protected DataType<?> getWidestType() {
    return getJsonType();
  }

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.MYSQL;
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> linkedHashMap) {
    throw new NotImplementedException();
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> linkedHashMap) {
    throw new NotImplementedException();
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    throw new NotImplementedException();
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> list, final Optional<ColumnId> optional) {
    throw new NotImplementedException();
  }

  @Override
  public String createSchema(final String schema) {
    throw new NotImplementedException();
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    throw new NotImplementedException();
  }
}
