package io.airbyte.integrations.destination.postgres.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;

public class PostgresSqlGenerator extends JdbcSqlGenerator {

  public static final DataType<?> JSONB_TYPE = new DefaultDataType<>(null, Object.class, "jsonb");

  public PostgresSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  @Override
  protected DataType<?> getStructType() {
    return JSONB_TYPE;
  }

  @Override
  protected DataType<?> getArrayType() {
    return JSONB_TYPE;
  }

  @Override
  protected DataType<?> getWidestType() {
    return JSONB_TYPE;
  }

  @Override
  protected SQLDialect getDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return null;
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    return null;
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return null;
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKey, final Optional<ColumnId> cursorField) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    return false;
  }
}
