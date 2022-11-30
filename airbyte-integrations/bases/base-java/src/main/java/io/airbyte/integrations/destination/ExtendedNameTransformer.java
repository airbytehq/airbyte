/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination;

/**
 * When choosing identifiers names in destinations, extended Names can handle more special
 * characters than standard Names by using the quoting characters: "..."
 *
 * This class detects when such special characters are used and adds the appropriate quoting when
 * necessary.
 */
public class ExtendedNameTransformer extends StandardNameTransformer {

  @Override
  public String convertStreamName(final String input) {
    return super.convertStreamName(input);
  }

  // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785)
  protected String disabled_convertStreamName(final String input) {
    if (useExtendedIdentifiers(input)) {
      return "\"" + input + "\"";
    } else {
      return applyDefaultCase(input);
    }
  }

  protected boolean useExtendedIdentifiers(final String input) {
    boolean result = false;
    if (input.matches("[^\\p{Alpha}_].*")) {
      result = true;
    } else if (input.matches(".*[^\\p{Alnum}_].*")) {
      result = true;
    }
    return result;
  }

}
