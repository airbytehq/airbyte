/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.db.mongodb.MongoUtils.MongoInstanceType.STANDALONE;
import static java.lang.Double.NaN;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.source.mongodb.MongoDbSource;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.bson.BsonArray;
import org.bson.BsonBinary;
import org.bson.BsonBoolean;
import org.bson.BsonDateTime;
import org.bson.BsonDecimal128;
import org.bson.BsonDocument;
import org.bson.BsonDouble;
import org.bson.BsonInt32;
import org.bson.BsonInt64;
import org.bson.BsonJavaScript;
import org.bson.BsonJavaScriptWithScope;
import org.bson.BsonObjectId;
import org.bson.BsonString;
import org.bson.BsonSymbol;
import org.bson.BsonTimestamp;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.utility.DockerImageName;

public class MongoDbSourceDataTypeTest {

  private static final String STREAM_NAME = "test.acceptance_test";
  private static final long MILLI = LocalDate.now().atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli();

  private MongoDBContainer mongoDBContainer;
  private MongoDatabase database;
  private JsonNode config;

  @BeforeEach
  public void setup() {
    mongoDBContainer = new MongoDBContainer(DockerImageName.parse("mongo:4.0.10"));
    mongoDBContainer.start();

    String connectionString = String.format("mongodb://%s:%s/",
        mongoDBContainer.getHost(),
        mongoDBContainer.getFirstMappedPort());

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", STANDALONE.getType())
        .put("host", mongoDBContainer.getHost())
        .put("port", mongoDBContainer.getFirstMappedPort())
        .put("tls", false)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put("database", "test")
        .put("auth_source", "admin")
        .build());

    database = new MongoDatabase(connectionString, "test");
    database.createCollection("acceptance_test");

    BsonDocument bsonDocument = new BsonDocument()
        .append("_id", new BsonObjectId(new ObjectId("61703280f3ca180ab088b574")))
        .append("boolean", BsonBoolean.TRUE)
        .append("int32", new BsonInt32(Integer.MAX_VALUE))
        .append("int64", new BsonInt64(Long.MAX_VALUE))
        .append("double", new BsonDouble(Double.MAX_VALUE))
        .append("decimal", new BsonDecimal128(Decimal128.NaN))
        .append("tms", new BsonTimestamp(MILLI))
        .append("dateTime", new BsonDateTime(MILLI))
        .append("binary", new BsonBinary(new UUID(10, 15)))
        .append("symbol", new BsonSymbol("s"))
        .append("string", new BsonString("test mongo db"))
        .append("objectId", new BsonObjectId(new ObjectId("6035210f35bd203721c3eab8")))
        .append("javaScript",
            new BsonJavaScript("var str = \"The best things in life are free\";\nvar patt = new RegExp(\"e\");\nvar res = patt.test(str);"))
        .append("javaScriptWithScope", new BsonJavaScriptWithScope("function (x){ return ++x; }",
            new BsonDocument().append("x1", new BsonInt32(256)).append("x2", new BsonInt32(142))))
        .append("document", new BsonDocument("test", new BsonString("let's test!")).append("number", new BsonInt32(1352)))
        .append("arrayWithDocs", new BsonArray(Arrays.asList(
            new BsonDocument().append("title", new BsonString("One Hundred Years of Solitude")).append("yearPublished", new BsonInt32(1967)),
            new BsonDocument().append("title", new BsonString("Chronicle of a Death Foretold")).append("yearPublished", new BsonInt32(1981)),
            new BsonDocument().append("title", new BsonString("Love in the Time of Cholera")).append("yearPublished", new BsonInt32(1985)))))
        .append("arrayWithStrings", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"), new BsonString("types"))));
    database.getDatabase().getCollection("acceptance_test", BsonDocument.class).insertOne(bsonDocument);
  }

  @AfterEach
  public void tearDown() throws Exception {
    database.close();
    mongoDBContainer.close();
  }

  @Test
  public void run() throws Exception {
    final List<AirbyteMessage> actualMessages =
        MoreIterators.toList(
            new MongoDbSource().read(config, getConfiguredCatalog(), Jsons.jsonNode(new HashMap<>())));

    setEmittedAtToNull(actualMessages);
    final List<AirbyteMessage> expectedMessages = getExpectedMessages();

    assertEquals(expectedMessages, actualMessages);
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withCursorField(Lists.newArrayList())
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withPrimaryKey(Lists.newArrayList())
            .withStream(CatalogHelpers.createAirbyteStream(
                "test.acceptance_test",
                Field.of("_id", JsonSchemaPrimitive.STRING),
                Field.of("boolean", JsonSchemaPrimitive.BOOLEAN),
                Field.of("int32", JsonSchemaPrimitive.NUMBER),
                Field.of("int64", JsonSchemaPrimitive.NUMBER),
                Field.of("double", JsonSchemaPrimitive.NUMBER),
                Field.of("decimal", JsonSchemaPrimitive.NUMBER),
                Field.of("tms", JsonSchemaPrimitive.STRING),
                Field.of("dateTime", JsonSchemaPrimitive.STRING),
                Field.of("binary", JsonSchemaPrimitive.STRING),
                Field.of("symbol", JsonSchemaPrimitive.STRING),
                Field.of("string", JsonSchemaPrimitive.STRING),
                Field.of("objectId", JsonSchemaPrimitive.STRING),
                Field.of("javaScript", JsonSchemaPrimitive.STRING),
                Field.of("javaScriptWithScope", JsonSchemaPrimitive.OBJECT),
                Field.of("document", JsonSchemaPrimitive.OBJECT),
                Field.of("arrayWithDocs", JsonSchemaPrimitive.ARRAY),
                Field.of("arrayWithStrings", JsonSchemaPrimitive.ARRAY))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL, SyncMode.FULL_REFRESH))
                .withSourceDefinedPrimaryKey(List.of(List.of("_id"))))));
  }

  private List<AirbyteMessage> getExpectedMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME)
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("_id", "61703280f3ca180ab088b574")
                    .put("boolean", true)
                    .put("int32", 2147483647)
                    .put("int64", 9223372036854775807L)
                    .put("double", 1.7976931348623157E308)
                    .put("decimal", NaN)
                    .put("tms", DataTypeUtils.toISO8601StringWithMilliseconds(MILLI))
                    .put("dateTime", DataTypeUtils.toISO8601StringWithMilliseconds(MILLI))
                    .put("binary", new BsonBinary(new UUID(10, 15)).getData())
                    .put("symbol", "s")
                    .put("string", "test mongo db")
                    .put("objectId", "6035210f35bd203721c3eab8")
                    .put("javaScript", "var str = \"The best things in life are free\";\nvar patt = new RegExp(\"e\");\nvar res = patt.test(str);")
                    .put("javaScriptWithScope", Jsons.jsonNode(ImmutableMap.of(
                        "code", "function (x){ return ++x; }",
                        "scope", Jsons.jsonNode(ImmutableMap.of("x1", 256, "x2", 142)))))
                    .put("document", Jsons.jsonNode(ImmutableMap.of("test", "let's test!", "number", 1352)))
                    .put("arrayWithDocs", Jsons.jsonNode(Lists.newArrayList(
                        Jsons.jsonNode(ImmutableMap.of("title", "One Hundred Years of Solitude", "yearPublished", 1967)),
                        Jsons.jsonNode(ImmutableMap.of("title", "Chronicle of a Death Foretold", "yearPublished", 1981)),
                        Jsons.jsonNode(ImmutableMap.of("title", "Love in the Time of Cholera", "yearPublished", 1985)))))
                    .put("arrayWithStrings", Jsons.jsonNode(Lists.newArrayList("test", "mongo", "types")))
                    .build()))));
  }

  private void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    for (final AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

}
