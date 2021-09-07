/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.mongodb;

import com.mongodb.client.MongoCollection;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import org.bson.Document;

class MongodbWriteConfig {

  private final String collectionName;
  private final String tmpCollectionName;
  private final DestinationSyncMode syncMode;
  private final MongoCollection<Document> collection;
  private final Set<String> documentsHash = new HashSet<>();

  MongodbWriteConfig(String collectionName,
                     String tmpCollectionName,
                     DestinationSyncMode syncMode,
                     MongoCollection<Document> collection,
                     Collection<String> documentsHash) {
    this.collectionName = collectionName;
    this.tmpCollectionName = tmpCollectionName;
    this.syncMode = syncMode;
    this.collection = collection;
    this.documentsHash.addAll(documentsHash);
  }

  public String getCollectionName() {
    return collectionName;
  }

  public String getTmpCollectionName() {
    return tmpCollectionName;
  }

  public DestinationSyncMode getSyncMode() {
    return syncMode;
  }

  public MongoCollection<Document> getCollection() {
    return collection;
  }

  public Set<String> getDocumentsHash() {
    return documentsHash;
  }

}
