/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import org.junit.jupiter.api.Test;

/**
 * Regression test for airbytehq/airbyte#76947.
 *
 * The {@code reserved_attribute_names} property was historically declared with
 * {@code airbyte_secret: true}, which masks its value in the UI on every connection edit.
 * Maintainers using the connector reported that they could not see the existing list of reserved
 * attribute names when adding or removing a single entry, and had to re-type the whole list.
 *
 * The field holds attribute names that collide with DynamoDB reserved keywords (see
 * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeNames.html).
 * It contains schema metadata, not credentials, so the secret marking was incorrect.
 *
 * This test pins the property's secret-ness at "false / absent" so a future edit cannot silently
 * re-introduce the masking.
 */
class DynamodbSpecTest {

  @Test
  void reservedAttributeNamesIsNotASecret() throws Exception {
    final String specJson = MoreResources.readResource("spec.json");
    final JsonNode spec = Jsons.deserialize(specJson);

    final JsonNode reservedAttrs = spec.path("connectionSpecification").path("properties").path("reserved_attribute_names");

    assertThat(reservedAttrs.isMissingNode()).as("reserved_attribute_names property must exist in spec.json").isFalse();

    // The property may either omit airbyte_secret entirely (preferred) or
    // explicitly set it to false. Either is fine; `true` is the regression.
    final JsonNode airbyteSecret = reservedAttrs.path("airbyte_secret");
    if (!airbyteSecret.isMissingNode()) {
      assertThat(airbyteSecret.asBoolean(true)).as("reserved_attribute_names must not be marked as a secret (see airbytehq/airbyte#76947)").isFalse();
    }
  }

}
