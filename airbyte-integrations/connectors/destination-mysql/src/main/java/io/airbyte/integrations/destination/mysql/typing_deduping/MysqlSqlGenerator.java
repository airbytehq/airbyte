package io.airbyte.integrations.destination.mysql.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.case_;
import static org.jooq.impl.DSL.cast;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.function;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.trueCondition;
import static org.jooq.impl.DSL.val;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.apache.commons.lang3.NotImplementedException;
import org.jooq.CaseConditionStep;
import org.jooq.Condition;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.InsertOnDuplicateStep;
import org.jooq.InsertReturningStep;
import org.jooq.Param;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.jooq.impl.DefaultDataType;
import org.jooq.impl.SQLDataType;

public class MysqlSqlGenerator extends JdbcSqlGenerator {

  public static final DefaultDataType<Object> JSON_TYPE = new DefaultDataType<>(null, Object.class, "json");

  public MysqlSqlGenerator(final NamingConventionTransformer namingResolver) {
    super(namingResolver);
  }

  private DataType<?> getJsonType() {
    return JSON_TYPE;
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
  protected List<Field<?>> extractRawDataFields(final LinkedHashMap<ColumnId, AirbyteType> columns, final boolean useExpensiveSaferCasting) {
    return columns
        .entrySet()
        .stream()
        .map(column -> {
          final String jsonExtractFunction;
          final AirbyteType type = column.getValue();
          final boolean isStruct = type instanceof Struct;
          final boolean isArray = type instanceof Array;
          if (type == AirbyteProtocolType.UNKNOWN || isStruct || isArray) {
            // UKKNOWN should use json_extract to retain the exact json value
            jsonExtractFunction = "JSON_EXTRACT";
          } else {
            // And primitive types should just use json_value, to (a) strip quotes from strings, and
            // (b) cast json null to sql null.
            jsonExtractFunction = "JSON_VALUE";
          }

          final Field<?> extractedValue = function(jsonExtractFunction, getJsonType(), field(name(COLUMN_NAME_DATA)), jsonPath(column.getKey()));
          if (isStruct) {
            return case_()
                .when(
                    extractedValue.isNull()
                        .or(function("JSON_TYPE", String.class, extractedValue).ne("OBJECT")),
                    val((Object) null)
                ).else_(extractedValue)
                .as(quotedName(column.getKey().name()));
          } else if (isArray) {
            return case_()
                .when(
                    extractedValue.isNull()
                        .or(function("JSON_TYPE", String.class, extractedValue).ne("ARRAY")),
                    val((Object) null)
                ).else_(extractedValue)
                .as(quotedName(column.getKey().name()));
          } else {
            final Field<?> castedValue = castedField(extractedValue, type, column.getKey().name());
            if (!(type instanceof final AirbyteProtocolType primitive)) {
              return castedValue;
            }
            return switch (primitive) {
              // These types are just casting to strings, so we need to use regex to validate their format
              case TIME_WITH_TIMEZONE -> case_()
                    .when(castedValue.notLikeRegex("^[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?([-+][0-9]{2}:[0-9]{2}|Z)$"), val((Object) null))
                    .else_(castedValue)
                  .as(quotedName(column.getKey().name()));
              case TIMESTAMP_WITH_TIMEZONE -> case_()
                  .when(castedValue.notLikeRegex("^[0-9]+-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?([-+][0-9]{2}:[0-9]{2}|Z)$"), val((Object) null))
                  .else_(castedValue)
                  .as(quotedName(column.getKey().name()));
              default -> castedValue;
            };
          }
        })
        .collect(Collectors.toList());
  }

  @Override
  protected Field<?> buildAirbyteMetaColumn(final LinkedHashMap<ColumnId, AirbyteType> columns) {
    // TODO Intentionally unimplemented for initial DV2 release
    return cast(val("{}"), getJsonType()).as(COLUMN_NAME_AB_META);
  }

  @Override
  protected Condition cdcDeletedAtNotNullCondition() {
    // TODO
    return trueCondition();
  }

  @Override
  protected Field<Integer> getRowNumber(final List<ColumnId> primaryKeys, final Optional<ColumnId> cursor) {
    // TODO
    return val(1).as(ROW_NUMBER_COLUMN_NAME);
  }

  @Override
  public Sql createSchema(final String schema) {
    throw new NotImplementedException();
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    throw new NotImplementedException();
  }

  @Override
  protected String beginTransaction() {
    return "START TRANSACTION";
  }

  @Override
  protected InsertReturningStep<Record> mutateInsertStatement(final InsertOnDuplicateStep<Record> insert) {
    // this turns the insert into an `INSERT IGNORE ...`
    // We're actually using this to ignore CAST() errors, rather than duplicate key errors.
    return insert.onDuplicateKeyIgnore();
  }

  private static Param<String> jsonPath(final ColumnId column) {
    // TODO escape jsonpath
    return val("$." + column.originalName());
  }
}
