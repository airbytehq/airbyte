package io.airbyte.integrations.source.dynamodb;

import java.net.URI;
import org.testcontainers.containers.localstack.LocalStackContainer;
import org.testcontainers.utility.DockerImageName;

public class DynamodbContainer extends LocalStackContainer {

    public static DynamodbContainer initWithStart() {
        var dynamodbContainer = (DynamodbContainer) new DynamodbContainer()
            .withServices(Service.DYNAMODB);
        dynamodbContainer.start();
        return dynamodbContainer;
    }

    public static DynamodbContainer init() {
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
