/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import io.airbyte.commons.text.Names;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;

public class ExasolSQLNameTransformer extends ExtendedNameTransformer {

  private static final Logger LOGGER = LoggerFactory.getLogger(ExasolSQLNameTransformer.class);

  @Override
  public String applyDefaultCase(final String input) {
    String result = input.toUpperCase();
    LOGGER.info("Apply default case for {} -> {}", input, result);
    return result;
  }

  @Override
  public String getRawTableName(final String streamName) {
    String result = super.getRawTableName(streamName);
    result = Names.doubleQuote(result); // Identifiers starting with _ must be quoted
    LOGGER.info("Get raw table name for stream {} -> {}", streamName, result);
    return result;
  }

  @Override
  public String getTmpTableName(final String streamName) {
    String result = super.getTmpTableName(streamName);
    result = Names.doubleQuote(result); // Identifiers starting with _ must be quoted
    LOGGER.info("Get temp table name for stream {} -> {}", streamName, result);
    return result;
  }

  @Override
  public String convertStreamName(final String input) {
    String result = input;
    if(result.startsWith("\"")) {
      result = result.substring(1);
    }
    if(result.endsWith("\"")) {
      result = result.substring(0, result.length()-1);
    }
    result = super.convertStreamName(result);
    result = Names.doubleQuote(result); // Identifiers starting with _ must be quoted
    LOGGER.info("Convert stream name {} -> {}", input, result);
    return result;
  }
}
