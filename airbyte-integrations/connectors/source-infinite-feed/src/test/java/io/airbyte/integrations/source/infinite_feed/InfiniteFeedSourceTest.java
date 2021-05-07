package io.airbyte.integrations.source.infinite_feed;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import org.junit.jupiter.api.Test;

public class InfiniteFeedSourceTest {
  @Test
  void test() {
    final AutoCloseableIterator<AirbyteMessage> read = new InfiniteFeedSource().read(
        Jsons.jsonNode(ImmutableMap.of("max_records", 10)),
        CatalogHelpers.toDefaultConfiguredCatalog(Jsons.clone(InfiniteFeedSource.CATALOG)),
        Jsons.emptyObject()
    );

    while(read.hasNext()) {
      System.out.println("read.next() = " + read.next());
    }
   }

}
