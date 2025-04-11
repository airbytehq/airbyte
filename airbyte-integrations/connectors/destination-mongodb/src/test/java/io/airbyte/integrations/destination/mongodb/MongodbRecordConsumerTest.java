/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.cdk.db.mongodb.MongoDatabase;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class MongodbRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs;

  @Mock
  private MongoDatabase mongoDatabase;

  @Mock
  private ConfiguredAirbyteCatalog catalog;

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @InjectMocks
  private MongodbRecordConsumer mongodbRecordConsumer;

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return mongodbRecordConsumer;
  }

  @Test
  void testCopyTableBatchProcessing() throws Exception {
    Method copyTableMethod = MongodbRecordConsumer.class.getDeclaredMethod("copyTable", 
        MongoDatabase.class, String.class, String.class);
    copyTableMethod.setAccessible(true);
    
    MongoCollection<Document> tempCollection = mock(MongoCollection.class);
    MongoCollection<Document> targetCollection = mock(MongoCollection.class);
    FindIterable<Document> findIterable = mock(FindIterable.class);
    MongoCursor<Document> cursor = mock(MongoCursor.class);
    
    List<Document> testDocuments = new ArrayList<>();
    for (int i = 0; i < 25000; i++) {
      testDocuments.add(new Document("test_field", "test_value_" + i));
    }
    
    when(mongoDatabase.getOrCreateNewCollection("temp_collection")).thenReturn(tempCollection);
    when(mongoDatabase.getOrCreateNewCollection("target_collection")).thenReturn(targetCollection);
    when(tempCollection.find()).thenReturn(findIterable);
    when(findIterable.projection(any())).thenReturn(findIterable);
    when(findIterable.iterator()).thenReturn(cursor);
    
    final int[] counter = {0};
    
    when(cursor.hasNext()).thenAnswer(invocation -> counter[0] < testDocuments.size());
    
    when(cursor.next()).thenAnswer(invocation -> {
      Document doc = testDocuments.get(counter[0]);
      counter[0]++;
      return doc;
    });
    
    copyTableMethod.invoke(null, mongoDatabase, "target_collection", "temp_collection");
    
    verify(targetCollection, times(3)).insertMany(anyList());
  }
}
