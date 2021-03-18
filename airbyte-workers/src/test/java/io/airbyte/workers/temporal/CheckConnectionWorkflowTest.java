package io.airbyte.workers.temporal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.temporal.api.common.v1.Payload;
import io.temporal.common.converter.DataConverter;
import io.temporal.common.converter.DefaultDataConverter;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class CheckConnectionWorkflowTest {
  @Test
  void test() {
    final IllegalStateException stateException = new IllegalStateException("bad state");
    final TemporalJobException temporalJobException = new TemporalJobException(Path.of("/tmp"), new IllegalStateException("bad state 2"));
    final Map<String, String> map = ImmutableMap.of("a", "1");
    final JsonNode jsonMap = Jsons.jsonNode(map);

    System.out.println("stateException = " + stateException);
    System.out.println("temporalJobException = " + temporalJobException);
    System.out.println("map = " + map);
    System.out.println("jsonMap = " + jsonMap);

    DataConverter converter = DataConverter.getDefaultInstance();

    final Optional<Payload> stateExceptionSerialized = converter.toPayload(stateException);
    final Optional<Payload> eSerialized = converter.toPayload(temporalJobException);
    final Optional<Payload> mapSerialized = converter.toPayload(map);
    final Optional<Payload> jsonMapSerialized = converter.toPayload(jsonMap);

    System.out.println("eSerialized = " + eSerialized);
    System.out.println("mapSerialized = " + mapSerialized);
    System.out.println("jsonMapSerialized = " + jsonMapSerialized);

    final IllegalStateException stateException1 = converter.fromPayload(stateExceptionSerialized.get(), IllegalStateException.class, IllegalStateException.class);
    final TemporalJobException temporalJobException1 = converter
        .fromPayload(eSerialized.get(), TemporalJobException.class, TemporalJobException.class);
    final Map map1 = converter.fromPayload(mapSerialized.get(), Map.class, Map.class);
    final JsonNode jsonMap1 = converter.fromPayload(jsonMapSerialized.get(), JsonNode.class, JsonNode.class);

    System.out.println("stateException1 = " + stateException1);
    System.out.println("temporalJobException1 = " + temporalJobException1);
    System.out.println("temporalJobException1.getLogPath() = " + temporalJobException1.getLogPath());
    System.out.println("map1 = " + map1);
    System.out.println("jsonMap1 = " + jsonMap1);
  }

}