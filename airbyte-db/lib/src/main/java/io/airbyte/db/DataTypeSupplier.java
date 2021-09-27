/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.SQLException;

@FunctionalInterface
public interface DataTypeSupplier<DataType> {

  DataType apply() throws SQLException;

}
