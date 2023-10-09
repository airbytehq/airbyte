/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db;

import java.sql.SQLException;
import org.jooq.DSLContext;

@FunctionalInterface
public interface ContextQueryFunction<T> {

  T query(DSLContext context) throws SQLException;

}
