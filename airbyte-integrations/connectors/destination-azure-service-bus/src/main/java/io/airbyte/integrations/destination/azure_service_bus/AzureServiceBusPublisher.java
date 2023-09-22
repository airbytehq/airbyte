package io.airbyte.integrations.destination.azure_service_bus;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Joiner;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.azure_service_bus.auth.SharedAccessKeyGenerator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import lombok.Getter;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;
import okhttp3.Call;
import okhttp3.ConnectionPool;
import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Request.Builder;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.ResponseBody;
import org.apache.commons.codec.binary.Base32;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;

@Slf4j
public class AzureServiceBusPublisher extends FailureTrackingAirbyteMessageConsumer {

  private final AzureServiceBusConfig serviceBusConfig;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final Base32 base32;
  private final MessageDigest md;
  private final HttpUrl queueUrl;
  private final SharedAccessKeyGenerator sasGenerator;

  private final OkHttpClient client;

  private final Map<AirbyteStreamNameNamespacePair, StreamProperties> streamValueMap = Maps.newHashMap();

  private AirbyteMessage lastMessage = null;

  public AzureServiceBusPublisher(final AzureServiceBusConfig serviceBusConfig,
      final ConfiguredAirbyteCatalog catalog,
      final Consumer<AirbyteMessage> outputRecordCollector) throws NoSuchAlgorithmException {
    this.outputRecordCollector = outputRecordCollector;
    this.serviceBusConfig = serviceBusConfig;
    this.catalog = catalog;
    queueUrl = serviceBusConfig.getEndpointUrl().newBuilder()
        .addPathSegment(serviceBusConfig.getQueueName())
        .build();
    sasGenerator = new SharedAccessKeyGenerator(serviceBusConfig.getSharedAccessKeyName(),
        serviceBusConfig.getSharedAccessKey());
    this.md = MessageDigest.getInstance("SHA-1");

    // 8 is not in Base32 set, and is an allowed character to use in a message ID (which doesn't support base64 chars)
    final byte PAD_DEFAULT = '8';
    base32 = new Base32(PAD_DEFAULT);

    client =  new OkHttpClient.Builder()
        .callTimeout(Duration.ofSeconds(180))
        .connectTimeout(40, TimeUnit.SECONDS)
        .writeTimeout(180, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build();

    log.info("initialized message publisher.");
  }

  @Override
  protected void startTracked() throws Exception {
    for (final ConfiguredAirbyteStream catalogStream : catalog.getStreams()) {
      String primaryKey = serializePrimaryKeyStruct(catalogStream.getPrimaryKey());
      log.info(
          "catalog primaryKey {}",
          primaryKey);
      log.info("catalogStream {}", catalogStream);

      AirbyteStreamNameNamespacePair streamNameNsPair = AirbyteStreamNameNamespacePair.fromAirbyteStream(
          catalogStream.getStream());

      streamValueMap.put(
          streamNameNsPair,
          StreamProperties.builder()
              .streamName(streamNameNsPair.getName())
              .streamNamespace(StringUtils.trimToEmpty(streamNameNsPair.getNamespace()))
              .primaryKeys(primaryKey)
              .build()
      );
    }
  }

  @NotNull
  static String serializePrimaryKeyStruct(List<List<String>> primaryKey) {
    if (primaryKey == null) {
      return StringUtils.EMPTY;
    }
    return Joiner.on(";").join(primaryKey.stream()
        .map(strList -> Joiner.on(",").join(strList))
        .toList());
  }

  @Override
  protected void acceptTracked(AirbyteMessage msg) throws Exception {
    if (msg.getType() == Type.STATE) {
      this.lastMessage = msg;
      return;
    } else if (msg.getType() != Type.RECORD) {
      log.warn("Unsupported airbyte message type: {}", msg.getType());
      return;
    }

    // type record:
    final AirbyteRecordMessage recordMessage = msg.getRecord();
    final AirbyteStreamNameNamespacePair streamKey = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!streamValueMap.containsKey(streamKey)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
    }
    StreamProperties streamValues = streamValueMap.get(streamKey);

    final Map<String, String> brokerPropsMap = new HashMap<>();

    // Service Bus provides a dedupe service via their message ID property – using dedupeMsgId
    // stops identical AirbyteMessage are singletons in the active service bus message queue
    final String dedupeMsgId = base32.encodeToString(
        md.digest(recordMessage.getData().toString().getBytes(StandardCharsets.UTF_8))
    );
    brokerPropsMap.put("MessageId", dedupeMsgId);
    brokerPropsMap.put("State", "Active");
    // Label enables the application to indicate the purpose of the message to the receiver
    brokerPropsMap.put("Label", streamValues.getStreamName());

    HttpUrl postMsgUrl = queueUrl.newBuilder()
        .addPathSegment("messages")
        .build();

    final JsonNode data = Jsons.jsonNode(ImmutableMap.of(
        JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(),
        JavaBaseConstants.COLUMN_NAME_DATA, recordMessage.getData(),
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt()));


    Builder requestBuilder = new Builder()
        .url(postMsgUrl)
        .post(RequestBody.create(Jsons.serialize(data).getBytes(StandardCharsets.UTF_8),
            MediaType.parse("application/json")));

    // add any additional properties from config
    serviceBusConfig.getAdditionalHeaders().forEach(requestBuilder::addHeader);

    addHeader(requestBuilder, AzureServiceBusDestination.STREAM, streamValues.getStreamName());
    addHeader(requestBuilder, AzureServiceBusDestination.NAMESPACE, streamValues.getStreamNamespace());
    addHeader(requestBuilder, AzureServiceBusDestination.KEYS, streamValues.getPrimaryKeys());
    requestBuilder.addHeader("BrokerProperties", Jsons.serialize(brokerPropsMap));

    requestBuilder.addHeader("Authorization",
        Objects.requireNonNull(sasGenerator.getToken(queueUrl.toString()), "require token").getToken());

    Request request = requestBuilder.build();
    log.info("sending request {}", request);
    Call call = client.newCall(request);
    try (Response response = call.execute()) {
      if (response.code() != 201) {
        ResponseBody body = response.body();
        String bodyStr = body == null ? "<empty>" : body.string();
        String errorMsg = "send message failed code=%d body=%s"
            .formatted(response.code(), bodyStr);
        throw new IllegalStateException(errorMsg);
      }
    }
  }

  private void addHeader(Builder requestBuilder, String headerName, String headerVal) {
    requestBuilder.addHeader(headerName, URLEncoder.encode(headerVal, StandardCharsets.UTF_8));
  }

  @SuppressWarnings("ConstantValue")
  @Override
  protected void close(boolean hasFailed) throws Exception {
    if (!hasFailed) {
      outputRecordCollector.accept(lastMessage);
    }

    ConnectionPool connectionPool = client.connectionPool();
    if (connectionPool != null) {
      connectionPool.evictAll();
    }
    log.info("shut down complete.");
  }


  @Getter
  @ToString
  @lombok.Builder
  static class StreamProperties {

    @NotNull
    String streamName;
    @NotNull
    String streamNamespace;
    @NotNull
    String primaryKeys;
  }

}
