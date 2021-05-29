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

package io.airbyte.integrations.destination.s3;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class S3Consumer extends FailureTrackingAirbyteMessageConsumer {

  private final S3DestinationConfig s3DestinationConfig;
  private final ConfiguredAirbyteCatalog configuredCatalog;
  private final Map<AirbyteStreamNameNamespacePair, S3Handler> streamNameAndNamespaceToHandlers;

  public S3Consumer(
                    S3DestinationConfig s3DestinationConfig,
                    ConfiguredAirbyteCatalog configuredCatalog) {
    this.s3DestinationConfig = s3DestinationConfig;
    this.configuredCatalog = configuredCatalog;
    this.streamNameAndNamespaceToHandlers = new HashMap<>(configuredCatalog.getStreams().size());
  }

  @Override
  protected void startTracked() throws Exception {
    AWSCredentials awsCreds = new BasicAWSCredentials(s3DestinationConfig.getAccessKeyId(),
        s3DestinationConfig.getSecretAccessKey());
    AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .withRegion(s3DestinationConfig.getBucketRegion())
        .build();
    Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    for (ConfiguredAirbyteStream configuredStream : configuredCatalog.getStreams()) {
      S3Handler handler = S3Handlers.getS3Handler(s3DestinationConfig, s3Client, configuredStream, uploadTimestamp);
      handler.initialize();

      AirbyteStream stream = configuredStream.getStream();
      AirbyteStreamNameNamespacePair streamNamePair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      streamNameAndNamespaceToHandlers.put(streamNamePair, handler);
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) throws Exception {
    if (airbyteMessage.getType() != Type.RECORD) {
      return;
    }

    AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
    AirbyteStreamNameNamespacePair pair = AirbyteStreamNameNamespacePair
        .fromRecordMessage(recordMessage);

    if (!streamNameAndNamespaceToHandlers.containsKey(pair)) {
      throw new IllegalArgumentException(
          String.format(
              "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
              Jsons.serialize(configuredCatalog), Jsons.serialize(recordMessage)));
    }

    UUID id = UUID.randomUUID();
    streamNameAndNamespaceToHandlers.get(pair).write(id, recordMessage);
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    for (S3Handler handler : streamNameAndNamespaceToHandlers.values()) {
      handler.close(hasFailed);
    }
  }

}
