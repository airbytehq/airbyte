package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public class DynamodbSshWrapper extends SshWrappedDestination {

  private String endPointKey;
  private final Destination delegate;


  public DynamodbSshWrapper(Destination delegate, String endPointKey) {
    super(delegate, endPointKey);
    this.delegate = delegate;
    this.endPointKey = endPointKey;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    try {
      DynamodbDestinationConfig dynamodbDestinationConfig = DynamodbDestinationConfig.getDynamodbDestinationConfig(config);
      String endpoint = dynamodbDestinationConfig.getEndpoint();
      ((ObjectNode)config).put(endPointKey, endpoint);
      return  SshTunnel.sshWrap(config, endPointKey, delegate::check);
    } catch (final ConnectionErrorException e) {
      final String sshErrorMessage = "Could not connect with provided SSH configuration. Error: " + e.getMessage();
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, sshErrorMessage);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(sshErrorMessage);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog catalog,
      final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {

    DynamodbDestinationConfig dynamodbDestinationConfig = DynamodbDestinationConfig.getDynamodbDestinationConfig(config);

    final SshTunnel tunnel = SshTunnel.getInstance(config, dynamodbDestinationConfig.getEndpoint());

    final AirbyteMessageConsumer delegateConsumer;
    try {
      delegateConsumer = delegate.getConsumer(tunnel.getConfigInTunnel(), catalog, outputRecordCollector);
    } catch (final Exception e) {
//      LOGGER.error("Exception occurred while getting the delegate consumer, closing SSH tunnel", e);
      tunnel.close();
      throw e;
    }
    return AirbyteMessageConsumer.appendOnClose(delegateConsumer, tunnel::close);
  }

}
