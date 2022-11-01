package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class DynamoDBContainer extends GenericContainer<DynamoDBContainer> {

  private static final DockerImageName DEFAULT_IMAGE_NAME = DockerImageName.parse("amazon/dynamodb-local");

  private static final String DEFAULT_TAG = "1.20.0";

  private static final int MAPPED_PORT = 8000;


  public DynamoDBContainer() {
    this(DEFAULT_IMAGE_NAME.withTag(DEFAULT_TAG));
  }


  public DynamoDBContainer(final DockerImageName dockerImageName) {
    super(dockerImageName);
    withExposedPorts(MAPPED_PORT);
  }

  /**
   * Gets a preconfigured {@link AmazonDynamoDB} client object for connecting to this
   * container.
   *
   * @return preconfigured client
   */
  public AmazonDynamoDB getClient() {
    return AmazonDynamoDBClientBuilder
        .standard()
        .withEndpointConfiguration(getEndpointConfiguration())
        .withCredentials(getCredentials())
        .build();
  }

  /**
   * Gets {@link AwsClientBuilder.EndpointConfiguration}
   * that may be used to connect to this container.
   *
   * @return endpoint configuration
   */
  public AwsClientBuilder.EndpointConfiguration getEndpointConfiguration() {
    return new AwsClientBuilder.EndpointConfiguration(
        "http://" + this.getHost() + ":" + this.getMappedPort(MAPPED_PORT),
        null
    );
  }

  /**
   * Gets an {@link AWSCredentialsProvider} that may be used to connect to this container.
   *
   * @return dummy AWS credentials
   */
  public AWSCredentialsProvider getCredentials() {
    return new AWSStaticCredentialsProvider(new BasicAWSCredentials("dummy", "dummy"));
  }

}
