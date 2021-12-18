package io.airbyte.commons.json_path;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.jayway.jsonpath.Configuration;
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.Option;
import com.jayway.jsonpath.spi.json.JacksonJsonNodeJsonProvider;
import com.jayway.jsonpath.spi.json.JacksonJsonProvider;
import com.jayway.jsonpath.spi.json.JsonProvider;
import com.jayway.jsonpath.spi.mapper.JacksonMappingProvider;
import com.jayway.jsonpath.spi.mapper.MappingProvider;
import io.airbyte.commons.json.Jsons;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class JsonPathsTest {

  @Test
  void test() {
    Configuration.setDefaults(new Configuration.Defaults() {

//      private final JsonProvider jsonProvider = new JacksonJsonProvider();
      private final JsonProvider jsonProvider = new JacksonJsonNodeJsonProvider();
      private final MappingProvider mappingProvider = new JacksonMappingProvider();

      @Override
      public JsonProvider jsonProvider() {
        return jsonProvider;
      }

      @Override
      public MappingProvider mappingProvider() {
        return mappingProvider;
      }

      @Override
      public Set<Option> options() {
        return EnumSet.of(Option.ALWAYS_RETURN_LIST);
      }
    });

//    final Configuration conf = Configuration.defaultConfiguration().addOptions(Option.ALWAYS_RETURN_LIST);
    final Configuration conf = Configuration.defaultConfiguration().addOptions(Option.AS_PATH_LIST);

    final String s = "{ \"alpha\": { \"beta\": [ \"charlie\", \"david\", \"epsilon\" ]} }";
    final ArrayNode read = JsonPath.parse(Jsons.deserialize(s)).read("$.alpha");
    System.out.println("read = " + read);
    System.out.println("read.get(0) = " + Jsons.jsonNode(read.get(0)));
    final ArrayNode read2 = JsonPath.using(conf).parse(Jsons.deserialize(s)).read("$.alpha.beta.[*]");
    System.out.println("read2 = " + read2);
  }
}