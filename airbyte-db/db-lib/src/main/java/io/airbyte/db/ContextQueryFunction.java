/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.SQLException;
import org.jooq.DSLContext;

@FunctionalInterface
public interface ContextQueryFunction<T> {

  T query(DSLContext context) throws SQLException;

}
