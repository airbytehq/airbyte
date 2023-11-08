/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import java.sql.SQLType;
import java.util.function.Supplier;
import javax.sql.DataSource;

public class RedshiftSqlGenerator extends JdbcSqlGenerator {

  public RedshiftSqlGenerator(final NamingConventionTransformer namingTransformer,
                              final SqlOperations sqlOperations,
                              final Supplier<DataSource> dataSourceSupplier) {
    super(namingTransformer, sqlOperations, dataSourceSupplier.get());
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

}
