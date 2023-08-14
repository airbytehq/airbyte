package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.LinkedHashMap;
import java.util.List;

public interface TypeAndDedupeQueryBuilder {

  String validatePrimaryKeys(final StreamId id,
                             final List<ColumnId> primaryKeys,
                             final LinkedHashMap<ColumnId, AirbyteType> streamColumns);

  String insertNewRecords(final StreamConfig stream, final String finalSuffix, final LinkedHashMap<ColumnId, AirbyteType> streamColumns);

  String dedupRawTable(final StreamId id, final String finalSuffix);

  String dedupFinalTable(final StreamId id,
                         final String finalSuffix,
                         final List<ColumnId> primaryKey,
                         final ColumnId cursor);

  String commitRawTable(final StreamId id);

  String cdcDeletes(final StreamConfig stream,
                    final String finalSuffix,
                    final LinkedHashMap<ColumnId, AirbyteType> streamColumns);

  default String declareMissingPrimaryKeyCountVariable() {
    return "DECLARE missing_pk_count BIGINT";
  }

  default String updateTableQuery(final StreamConfig stream, final String finalSuffix, final boolean verifyPrimaryKeys) {
    String pkVarDeclaration = "";
    String validatePrimaryKeys = "";
    if (verifyPrimaryKeys && stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      pkVarDeclaration = declareMissingPrimaryKeyCountVariable();
      validatePrimaryKeys = validatePrimaryKeys(stream.id(), stream.primaryKey(), stream.columns());
    }
    final String insertNewRecords = insertNewRecords(stream, finalSuffix, stream.columns());
    String dedupFinalTable = "";
    String cdcDeletes = "";
    String dedupRawTable = "";
    if (stream.destinationSyncMode() == DestinationSyncMode.APPEND_DEDUP) {
      dedupRawTable = dedupRawTable(stream.id(), finalSuffix);
      // If we're in dedup mode, then we must have a cursor
      dedupFinalTable = dedupFinalTable(stream.id(), finalSuffix, stream.primaryKey(), stream.cursor().get());
      cdcDeletes = cdcDeletes(stream, finalSuffix, stream.columns());
    }
    final String commitRawTable = commitRawTable(stream.id());

//    return new StringSubstitutor(Map.of(
//        "pk_var_declaration", pkVarDeclaration,
//        "validate_primary_keys", validatePrimaryKeys,
//        "insert_new_records", insertNewRecords,
//        "dedup_final_table", dedupFinalTable,
//        "cdc_deletes", cdcDeletes,
//        "dedupe_raw_table", dedupRawTable,
//        "commit_raw_table", commitRawTable)).replace(
//        """
//        ${pk_var_declaration}
//        BEGIN TRANSACTION;
//
//        ${validate_primary_keys}
//
//        ${insert_new_records}
//
//        ${dedup_final_table}
//
//        ${dedupe_raw_table}
//
//        ${cdc_deletes}
//
//        ${commit_raw_table}
//
//        COMMIT;
//        """);

    return String.join("\n\n",
                       pkVarDeclaration,
                       "BEGIN TRANSACTION;",
                       validatePrimaryKeys,
                       insertNewRecords,
                       dedupFinalTable,
                       cdcDeletes,
                       dedupRawTable,
                       commitRawTable,
                       "COMMIT;"
    );
  }
  }


}
