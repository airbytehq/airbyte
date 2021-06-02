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

package io.airbyte.integrations.destination.s3.csv;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.DATE_FORMAT;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.DeleteObjectsResult;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3OutputFormatter;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3CsvOutputFormatter implements S3OutputFormatter {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3CsvOutputFormatter.class);
  private static final ExtendedNameTransformer NAME_TRANSFORMER = new ExtendedNameTransformer();

  private final S3DestinationConfig config;
  private final S3CsvFormatConfig formatConfig;
  private final AmazonS3 s3Client;
  private final AirbyteStream stream;
  private final DestinationSyncMode syncMode;
  private final List<String> sortedHeaders;
  private final String outputPrefix;
  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final CSVPrinter csvPrinter;

  public S3CsvOutputFormatter(S3DestinationConfig config,
                              AmazonS3 s3Client,
                              ConfiguredAirbyteStream configuredStream,
                              Timestamp uploadTimestamp)
      throws IOException {
    this.config = config;
    this.formatConfig = (S3CsvFormatConfig) config.getFormatConfig();
    this.s3Client = s3Client;
    this.stream = configuredStream.getStream();
    this.syncMode = configuredStream.getDestinationSyncMode();
    this.sortedHeaders = getSortedFields(configuredStream.getStream().getJsonSchema(),
        formatConfig);

    // prefix: <bucket-path>/<source-namespace-if-exists>/<stream-name>
    // filename: <upload-date>-<upload-millis>.csv
    // full path: <bucket-name>/<prefix>/<filename>
    this.outputPrefix = getOutputPrefix(config.getBucketPath(), stream);
    String outputFilename = getOutputFilename(uploadTimestamp);
    String objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': {}/{}", stream.getName(), config.getBucketName(),
        objectKey);

    // The stream transfer manager lets us greedily stream into S3. The native AWS SDK does not
    // have support for streaming multipart uploads. The alternative is first writing the entire
    // output to disk before loading into S3. This is not feasible with large input.
    // Data is chunked into parts during the upload. A part is sent off to a queue to be uploaded
    // once it has reached it's configured part size.
    // See {@link S3DestinationConstants} for memory usage calculation.
    this.uploadManager = new StreamTransferManager(config.getBucketName(), objectKey, s3Client)
        .numStreams(S3DestinationConstants.DEFAULT_NUM_STREAMS)
        .queueCapacity(S3DestinationConstants.DEFAULT_QUEUE_CAPACITY)
        .numUploadThreads(S3DestinationConstants.DEFAULT_UPLOAD_THREADS)
        .partSize(S3DestinationConstants.DEFAULT_PART_SIZE_MD);
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    this.outputStream = uploadManager.getMultiPartOutputStreams().get(0);
    this.csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8),
        CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
            .withHeader(getHeaders(sortedHeaders).toArray(new String[0])));
  }

  /**
   * Get a sorted field list in the json object so that this object can be iterated through with a
   * defined order later on.
   */
  static List<String> getSortedFields(JsonNode jsonSchema, S3CsvFormatConfig formatConfig) {
    // When no flattening is needed, we do not care about iteration order.
    if (formatConfig.getFlattening() == Flattening.NO) {
      return Collections.emptyList();
    }
    if (formatConfig.getFlattening() == Flattening.ROOT_LEVEL) {
      return MoreIterators.toList(jsonSchema.get("properties").fieldNames())
          .stream().sorted().collect(Collectors.toList());
    }
    throw new IllegalArgumentException(
        "Unexpected flattening config: " + formatConfig.getFlattening());
  }

  static String getOutputPrefix(String bucketPath, AirbyteStream stream) {
    return getOutputPrefix(bucketPath, stream.getNamespace(), stream.getName());
  }

  @VisibleForTesting
  public static String getOutputPrefix(String bucketPath, String namespace, String streamName) {
    List<String> paths = new LinkedList<>();

    if (bucketPath != null) {
      paths.add(bucketPath);
    }
    if (namespace != null) {
      paths.add(NAME_TRANSFORMER.convertStreamName(namespace));
    }
    paths.add(NAME_TRANSFORMER.convertStreamName(streamName));

    return String.join("/", paths);
  }

  static String getOutputFilename(Timestamp timestamp) {
    return String.format("%s_%d.csv", DATE_FORMAT.format(timestamp), timestamp.getTime());
  }

  /**
   * When there exists sorted headers from input stream, replace {@code
   * JavaBaseConstants.COLUMN_NAME_DATA} with those headers.
   */
  static List<String> getHeaders(List<String> sortedHeaders) {
    List<String> headers = Lists.newArrayList(JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    if (sortedHeaders.isEmpty()) {
      headers.add(JavaBaseConstants.COLUMN_NAME_DATA);
    } else {
      headers.addAll(sortedHeaders);
    }
    return headers;
  }

  static List<String> getCsvData(S3CsvFormatConfig formatConfig,
                                 List<String> sortedHeaders,
                                 JsonNode json) {
    if (formatConfig.getFlattening() == Flattening.NO) {
      return Collections.singletonList(Jsons.serialize(json));
    }

    if (formatConfig.getFlattening() == Flattening.ROOT_LEVEL) {
      List<String> values = new LinkedList<>();
      for (String field : sortedHeaders) {
        JsonNode value = json.get(field);
        if (value == null) {
          values.add("");
        } else if (value.isValueNode()) {
          // Call asText method on value nodes so that proper string
          // representation of json values can be returned by Jackson.
          // Otherwise, CSV printer will just call the toString method,
          // which can be problematic (e.g. text node will have extra
          // double quotation marks around its text value).
          values.add(value.asText());
        } else {
          values.add(Jsons.serialize(value));
        }
      }

      return values;
    }

    throw new IllegalArgumentException(
        "Unexpected flattening config: " + formatConfig.getFlattening());
  }

  /**
   * <li>1. Create bucket if necessary.</li>
   * <li>2. Under OVERWRITE mode, delete all objects with the output prefix.</li>
   */
  @Override
  public void initialize() {
    String bucket = config.getBucketName();
    if (!s3Client.doesBucketExistV2(bucket)) {
      LOGGER.info("Bucket {} does not exist; creating...", bucket);
      s3Client.createBucket(bucket);
      LOGGER.info("Bucket {} has been created.", bucket);
    }

    if (syncMode == DestinationSyncMode.OVERWRITE) {
      LOGGER.info("Overwrite mode");
      List<KeyVersion> keysToDelete = new LinkedList<>();
      List<S3ObjectSummary> objects = s3Client.listObjects(bucket, outputPrefix)
          .getObjectSummaries();
      for (S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Purging non-empty output path for stream '{}' under OVERWRITE mode...",
            stream.getName());
        DeleteObjectsResult result = s3Client
            .deleteObjects(new DeleteObjectsRequest(bucket).withKeys(keysToDelete));
        LOGGER.info("Deleted {} file(s) for stream '{}'.", result.getDeletedObjects().size(),
            stream.getName());
      }
    }
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) throws IOException {
    List<Object> data = new LinkedList<>();
    data.add(id);
    data.add(recordMessage.getEmittedAt());
    data.addAll(getCsvData(formatConfig, sortedHeaders, recordMessage.getData()));
    csvPrinter.printRecord(data);
  }

  @Override
  public void close(boolean hasFailed) throws IOException {
    if (hasFailed) {
      LOGGER.warn("Failure detected. Aborting upload of stream '{}'...", stream.getName());
      csvPrinter.close();
      outputStream.close();
      uploadManager.abort();
      LOGGER.warn("Upload of stream '{}' aborted.", stream.getName());
    } else {
      LOGGER.info("Uploading remaining data for stream '{}'.", stream.getName());
      csvPrinter.close();
      outputStream.close();
      uploadManager.complete();
      LOGGER.info("Upload completed for stream '{}'.", stream.getName());
    }
  }

}
