/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.jdbc;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.text.Names;
import org.jetbrains.annotations.NotNull;

public class SingleStoreNamingTransformer implements NamingConventionTransformer {

  @NotNull
  @Override
  public String applyDefaultCase(@NotNull String name) {
    return name.toLowerCase();
  }

  @NotNull
  @Override
  public String getIdentifier(@NotNull String name) {
    return truncate(convertStreamName(name));
  }

  @NotNull
  @Override
  public String getNamespace(@NotNull String namespace) {
    return convertStreamName(namespace);
  }

  @Deprecated
  @NotNull
  @Override
  public String getRawTableName(@NotNull String name) {
    return convertStreamName(String.format("_airbyte_raw_%s", name));
  }

  @Deprecated
  @NotNull
  @Override
  public String getTmpTableName(@NotNull String name) {
    return convertStreamName(Strings.addRandomSuffix("_airbyte_tmp", "_", 3) + "_" + name);
  }

  @NotNull
  @Override
  public String convertStreamName(@NotNull String input) {
    return Names.toAlphanumericAndUnderscore(input);
  }

  // SingleStore support 256 max length of names but set 64 as version below than 8.5.0 is limited by
  // 64
  private String truncate(String str) {
    return str.substring(0, Math.min(str.length(), 64));
  }

}
