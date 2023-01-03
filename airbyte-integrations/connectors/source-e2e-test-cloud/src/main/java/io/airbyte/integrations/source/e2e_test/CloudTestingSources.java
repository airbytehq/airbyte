/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

/**
 * Since 2.0.0, the cloud version is the same as the OSS version. This connector should be removed.
 */
public class CloudTestingSources extends SpecModifyingSource implements Source {

  private static final String CLOUD_TESTING_SOURCES_TITLE = "Cloud E2E Test Source Spec";

  public CloudTestingSources() {
    super(new TestingSources());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new CloudTestingSources();
    new IntegrationRunner(source).run(args);
  }

  /**
   * 1. Update the title. 2. Only keep the "continuous feed" mode.
   */
  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification()).put("title", CLOUD_TESTING_SOURCES_TITLE);
    return spec;
  }

}
