/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import java.net.URI;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.utility.DockerImageName;

public class DynamodbContainer extends LocalStackContainer {

  public static DynamodbContainer createWithStart() {
    var dynamodbContainer = (DynamodbContainer) new DynamodbContainer()
        .withServices(Service.DYNAMODB);
    dynamodbContainer.start();
    return dynamodbContainer;
  }

  public static DynamodbContainer create() {
    return (DynamodbContainer) new DynamodbContainer()
        .withServices(Service.DYNAMODB);
  }

  public DynamodbContainer() {
    super(DockerImageName.parse("localstack/localstack:1.2.0"));
  }

  public URI getEndpointOverride() {
    return super.getEndpointOverride(Service.DYNAMODB);
  }

}
