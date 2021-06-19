package io.airbyte.commons.mapper;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

public class MoreMappers {

  public static ObjectMapper initMapper() {
    final ObjectMapper result = new ObjectMapper().registerModule(new JavaTimeModule());
    result.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    return result;
  }

  public static ObjectMapper initYamlMapper(YAMLFactory factory) {
    return new ObjectMapper(factory).registerModule(new JavaTimeModule());
  }

}
