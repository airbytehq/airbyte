/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLType;
import java.time.Instant;
import java.util.Optional;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer) {
    super(namingTransformer);
  }

  @Override
  protected String vendorId() {
    return "REDSHIFT";
  }

  @Override
  protected SQLType widestType() {
    // Vendor specific stuff I don't think matters for us since we're just pulling out the name
    return new CustomSqlType("SUPER", vendorId(), 123);
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    return false;
  }

  @Override
  public String updateTable(final StreamConfig stream,
                            final String finalSuffix,
                            final Optional<Instant> minRawTimestamp,
                            final boolean useExpensiveSaferCasting) {
    return null;
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return null;
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return null;
  }

  @Override
  public String clearLoadedAt(final StreamId streamId) {
    return null;
  }

}
