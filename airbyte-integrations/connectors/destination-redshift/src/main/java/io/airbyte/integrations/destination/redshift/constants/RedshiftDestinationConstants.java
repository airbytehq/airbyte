/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.constants;

import org.jooq.DataType;
import org.jooq.impl.DefaultDataType;

/**
 * Constant holder for Redshift Destination
 */
public class RedshiftDestinationConstants {

  private RedshiftDestinationConstants() {}

  public static final String UPLOADING_METHOD = "uploading_method";

  public static final DataType<String> SUPER_TYPE = new DefaultDataType<>(null, String.class, "super");

  public static final String DROP_CASCADE_OPTION = "drop_cascade";

}
