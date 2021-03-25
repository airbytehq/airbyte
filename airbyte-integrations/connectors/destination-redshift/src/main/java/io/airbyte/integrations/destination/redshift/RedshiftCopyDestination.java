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

package io.airbyte.integrations.destination.redshift;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.CreateBucketRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.FailureTrackingConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.ArrayList;
import java.util.Map;

/**
 * A more efficient Redshift Destination than the sql-based {@link RedshiftDestination}. Instead of
 * inserting data as batched SQL INSERTs, we follow Redshift best practices and, 1) Stream the data
 * to S3. One compressed file is created per table. 2) Copy the S3 file to Redshift. See
 * https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-use-copy.html for more info.
 *
 * Although Redshift recommends splitting the file for more efficient copying, this introduces
 * complexity around file partitioning that should be handled by a file destination connector. The
 * single file approach is orders of magnitude faster than batch inserting and 'good-enough' for
 * now.
 */
public class RedshiftCopyDestination implements Destination {

  // TODO: figure out a way to consistently randomise this bucket
  public static String DEFAULT_AIRBYTE_STAGING_S3_BUCKET = "airbyte.staging";
  private static final StandardNameTransformer namingResolver = new StandardNameTransformer();

  /**
   * This flow does not currently let users configure a staging bucket.
   */
  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    var redshiftRegion = extractRegionFromRedshiftUrl("");
    var awsCreds = new BasicAWSCredentials("", "");

    var client = AmazonS3ClientBuilder.standard()
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds)).withRegion(redshiftRegion)
        .build();

    return new RedshiftCopyDestinationConsumer(client, redshiftRegion, catalog);
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    // TODO: implement
    // this returns the spec
    return null;
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    // TODO: implement
    // this should check the config is correct;
    // 1. S3 credentials are present
    // - should be able to create and destroy bucket
    // - should be able to write and delete object
    // 2. Redshift credentials are present
    // - should be able to create, rename and delete table
    // - should be able to write records
    return null;
  }

  /**
   * Redshift urls are of the form <cluster-name>.<cluster-id>.<region>.redshift.amazon.com.
   * Extracting region from the url is currently the simplest way to figure out a cluster's region.
   * Although unlikely, might break if the url schema changes.
   */
  @VisibleForTesting
  static String extractRegionFromRedshiftUrl(String url) {
    // TODO: validate the url?
    var split = url.split("\\.");
    return split[2];
  }

  @VisibleForTesting
  static void createS3StagingBucketIfNeeded(AmazonS3 client, String region) {
    var stagingBucketMissing = !client.doesBucketExistV2(DEFAULT_AIRBYTE_STAGING_S3_BUCKET);
    if (stagingBucketMissing) {
      var createBucketRequest = new CreateBucketRequest(DEFAULT_AIRBYTE_STAGING_S3_BUCKET, region);
      client.createBucket(createBucketRequest);
    }
  }

  private static class RedshiftCopyDestinationConsumer extends FailureTrackingConsumer<AirbyteMessage> {

    private final AmazonS3 client;
    private final ConfiguredAirbyteCatalog catalog;
    private final String redshiftRegion;
    private Map<String, RedshiftCopier> tableNameToCopier;

    public RedshiftCopyDestinationConsumer(AmazonS3 client, String redshiftRegion, ConfiguredAirbyteCatalog catalog) {
      this.client = client;
      this.catalog = catalog;
      this.redshiftRegion = redshiftRegion;
    }

    @Override
    protected void startTracked() throws Exception {
      createS3StagingBucketIfNeeded(client, redshiftRegion);

      // write to bucket
      for (var stream : catalog.getStreams()) {
        var streamName = stream.getStream().getName();
        var tableName = namingResolver.getRawTableName(streamName);
        var tmpTableName = namingResolver.getTmpTableName(streamName);

      }
    }

    @Override
    protected void acceptTracked(AirbyteMessage message) throws Exception {
      if (message.getType() == AirbyteMessage.Type.RECORD) {
        if (tableNameToCopier.containsKey(message.getRecord().getStream())) {
          throw new IllegalArgumentException(
              String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                  Jsons.serialize(catalog), Jsons.serialize(message)));
        }

        var tableName = message.getRecord().getStream();
        tableNameToCopier.get(tableName).uploadToS3(message.getRecord());
      }
    }

    /**
     * Although 'close' suggests a focus on clean up, this method also loads S3 files into Redshift.
     * First, move the files into temporary table, then merge the temporary tables with the final
     * destination tables. Lastly, do actual clean up and best-effort remove the S3 files and temporary
     * tables.
     */
    @Override
    protected void close(boolean hasFailed) throws Exception {
      RedshiftCopier.closeAsOneTransaction(new ArrayList<>(tableNameToCopier.values()), hasFailed, null);
    }

  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new RedshiftCopyDestination()).run(args);
  }

}
