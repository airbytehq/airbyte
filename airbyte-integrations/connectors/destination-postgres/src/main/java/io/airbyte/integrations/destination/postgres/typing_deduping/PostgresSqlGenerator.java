package io.airbyte.integrations.destination.postgres.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.rowNumber;
import static org.jooq.impl.DSL.val;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

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
    return columns
        .entrySet()
        .stream()
        .map(column -> castedField(
            extractColumnAsText(column.getKey()),
            column.getValue(),
            column.getKey().name(),
            useExpensiveSaferCasting))
        .collect(Collectors.toList());
  }

  @Override
  protected Field<?> castedField(
      final Field<?> field,
      final AirbyteType type,
      final String alias,
      final boolean useExpensiveSaferCasting) {
    final DataType<?> dialectType = toDialectType(type);
    if (useExpensiveSaferCasting) {
      return function("airbyte_safe_cast", dialectType, field).as(quotedName(alias));
    } else {
      return cast(field, dialectType).as(quotedName(alias));
    }
  }

  // TODO this isn't actually used right now... can we refactor this out?
  // (redshift is doing something interesting with this method, so leaving it for now)
  @Override
  protected Field<?> castedField(final Field<?> field, final AirbyteProtocolType type, final boolean useExpensiveSaferCasting) {
    return cast(field, toDialectType(type));
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    // TODO
    return cast("{}", JSONB_TYPE).as(COLUMN_NAME_AB_META);
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    return field(name(COLUMN_NAME_AB_LOADED_AT)).isNotNull()
        .and(function("JSONB_TYPEOF", SQLDataType.VARCHAR, extractColumnAsJson(cdcDeletedAtColumn))
            .ne("null"));
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    // literally identical to redshift's getRowNumber implementation, changes here probably should
    // be reflected there
    final List<Field<?>> primaryKeyFields =
        primaryKeys != null ? primaryKeys.stream().map(columnId -> field(quotedName(columnId.name()))).collect(Collectors.toList())
            : new ArrayList<>();
    final List<Field<?>> orderedFields = new ArrayList<>();
    // We can still use Jooq's field to get the quoted name with raw sql templating.
    // jooq's .desc returns SortField<?> instead of Field<?> and NULLS LAST doesn't work with it
    cursor.ifPresent(columnId -> orderedFields.add(field("{0} desc NULLS LAST", field(quotedName(columnId.name())))));
    orderedFields.add(field("{0} desc", quotedName(COLUMN_NAME_AB_EXTRACTED_AT)));
    return rowNumber()
        .over()
        .partitionBy(primaryKeyFields)
        .orderBy(orderedFields).as(ROW_NUMBER_COLUMN_NAME);
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // TODO
    return false;
  }

  /**
   * Extract a raw field and cast it to text
   */
  private Field<?> extractColumnAsText(final ColumnId column) {
    return field("{0} ->> {1}", name(COLUMN_NAME_DATA), val(column.originalName()));
  }

  /**
   * Extract a raw field, leaving it as jsonb
   */
  private Field<?> extractColumnAsJson(final ColumnId column) {
    return field("{0} -> {1}", name(COLUMN_NAME_DATA), val(column.originalName()));
  }
}
