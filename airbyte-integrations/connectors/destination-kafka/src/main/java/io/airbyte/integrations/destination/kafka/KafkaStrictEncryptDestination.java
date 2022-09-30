package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class KafkaStrictEncryptDestination extends SpecModifyingDestination {

  private static final ObjectMapper MAPPER = new ObjectMapper();
  private static final Set<String> SECURE_KAFKA_PROTOCOLS = Set.of(KafkaProtocol.SASL_SSL.name());
  private static final Set<String> SECURE_PROTOCOLS = Set.of("SSL");

  public KafkaStrictEncryptDestination() {
    super(new KafkaDestination());
  }

  @Override
  public ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ObjectNode protocolConfigNode = (ObjectNode) spec.getConnectionSpecification().get("properties").get("protocol");

    ArrayNode protocols = (ArrayNode) protocolConfigNode.get("oneOf");
    ArrayNode filteredProtocols = MAPPER.createArrayNode();
    for (JsonNode protocol : protocols) {
      if (SECURE_KAFKA_PROTOCOLS.contains(protocol.get("properties").get("security_protocol").get("default").asText())) {
        filteredProtocols.add(protocol);
      }
    }

    protocolConfigNode.set("oneOf", filteredProtocols);
    return spec;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    // Bootstrap servers may specify a protocol. For example, these are both valid configs:
    //   foo.com:1234,bar.com:1234,baz.com:1234
    //   PLAINTEXT://foo.com:1234,SSL://bar.com:1234,baz.com:1234
    // If the connection protocol is specified, we should require it to be SSL.
    String[] bootstrapServers = config.get("bootstrap_servers").asText().split(",");
    List<String> unsecuredServers = new ArrayList<>();
    for (String bootstrapServer : bootstrapServers) {
      int protocolSeparatorIndex = bootstrapServer.indexOf("://");
      if (protocolSeparatorIndex != -1) {
        String protocol = bootstrapServer.substring(0, protocolSeparatorIndex);
        if (!SECURE_PROTOCOLS.contains(protocol)) {
          unsecuredServers.add(bootstrapServer);
        }
      }
    }
    if (!unsecuredServers.isEmpty()) {
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Unsecured connection to bootstrap servers is not allowed. These servers specify an insecure connection protocol: " + unsecuredServers);
    }

    return super.check(config);
  }
}
