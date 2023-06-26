/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.collect.ImmutableList;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.UnsupportedOneOf;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import org.junit.jupiter.api.Test;

public class BigQuerySqlGeneratorTest {

  @Test
  public void testToDialectType() {
    final BigQuerySqlGenerator generator = new BigQuerySqlGenerator();
    final Struct s = new Struct(new LinkedHashMap<>());
    final Array a = new Array(AirbyteProtocolType.BOOLEAN);

    assertEquals(StandardSQLTypeName.INT64, generator.toDialectType((AirbyteType) AirbyteProtocolType.INTEGER));
    assertEquals(StandardSQLTypeName.JSON, generator.toDialectType(s));
    assertEquals(StandardSQLTypeName.JSON, generator.toDialectType(a));
    assertEquals(StandardSQLTypeName.JSON, generator.toDialectType(new UnsupportedOneOf(new ArrayList<>())));

    OneOf o = new OneOf(ImmutableList.of(s));
    assertEquals(StandardSQLTypeName.JSON, generator.toDialectType(o));
    o = new OneOf(ImmutableList.of(a));
    assertEquals(StandardSQLTypeName.JSON, generator.toDialectType(o));
    o = new OneOf(ImmutableList.of(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.NUMBER));
    assertEquals(StandardSQLTypeName.NUMERIC, generator.toDialectType(o));
  }

}
