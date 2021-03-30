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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream.DestinationSyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Properties;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@Disabled("Disabled on automatic execution as the tests requires specific credentials to run."
    + "Intended to be a lighter-weight complement to the Docker integration tests. Fill in the appropriate blank variables to run.")
public class RedshiftCopierTest {

  // Either fill up these variables or fill up the config file before running.
  private static String S3_KEY_ID = "";
  private static String S3_KEY = "";
  private static String REDSHIFT_CONNECTION_STRING = "";
  private static String REDSHIFT_USER = "";
  private static String REDSHIFT_PASS = "";

  private static final String S3_REGION = "us-west-2";
  private static final String TEST_BUCKET = "airbyte-redshift-integration-tests";
  private static final String RUN_FOLDER = "test-folder";
  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "redshift_copier_test";
  private static final String RAW_TABLE_NAME = new RedshiftSQLNameTransformer().getRawTableName(STREAM_NAME);

  private static final ObjectMapper mapper = new ObjectMapper();

  private static AmazonS3 s3Client;
  private static JdbcDatabase redshiftDb;

  @BeforeAll
  public static void setUp() {
    readConfigFile();
    var awsCreds = new BasicAWSCredentials(S3_KEY_ID, S3_KEY);
    s3Client = AmazonS3ClientBuilder.standard()
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds)).withRegion(S3_REGION)
        .build();

    if (!s3Client.doesBucketExistV2(TEST_BUCKET)) {
      s3Client.createBucket(TEST_BUCKET);
    }

    redshiftDb = Databases.createRedshiftDatabase(REDSHIFT_USER, REDSHIFT_PASS, REDSHIFT_CONNECTION_STRING);
  }

  private static void readConfigFile() {
    Properties prop = new Properties();
    String propFileName = "config.properties";
    var inputStream = RedshiftCopierTest.class.getClassLoader().getResourceAsStream(propFileName);
    if (inputStream != null) {
      try {
        prop.load(inputStream);

        S3_KEY_ID = prop.getProperty("s3.keyId");
        S3_KEY = prop.getProperty("s3.accessKey");
        REDSHIFT_CONNECTION_STRING = prop.getProperty("redshift.connString");
        REDSHIFT_USER = prop.getProperty("redshift.user");
        REDSHIFT_PASS = prop.getProperty("redshift.pass");
      } catch (IOException e) {
        e.printStackTrace();
      }
    }

  }

  @BeforeEach
  public void reset() throws SQLException {
    var sqlOp = new RedshiftSqlOperations();
    sqlOp.dropTableIfExists(redshiftDb, SCHEMA_NAME, RAW_TABLE_NAME);
  }

  @AfterAll
  public static void tearDown() {
    if (!s3Client.doesBucketExistV2(TEST_BUCKET)) {
      s3Client.deleteBucket(TEST_BUCKET);
    }
  }

  @Test
  @DisplayName("When OVERWRITE should wipe table before appending new data")
  public void destSyncModeOverwriteTest() throws Exception {
    var copier = new RedshiftCopier(TEST_BUCKET, RUN_FOLDER, DestinationSyncMode.OVERWRITE, SCHEMA_NAME, STREAM_NAME, s3Client, redshiftDb, S3_KEY_ID,
        S3_KEY, S3_REGION);

    AirbyteRecordMessage msg = getAirbyteRecordMessage();

    copier.uploadToS3(msg);
    RedshiftCopier.closeAsOneTransaction(List.of(copier), false, redshiftDb);

    assertFalse(s3Client.doesObjectExist(TEST_BUCKET, RUN_FOLDER + "/" + STREAM_NAME));

    var recordList = redshiftDb.bufferedResultSetQuery(
        connection -> {
          final String sql = "SELECT * FROM " + RAW_TABLE_NAME + ";";
          return connection.prepareStatement(sql).executeQuery();
        },
        JdbcUtils::rowToJson);

    assertEquals(1, recordList.size());
  }

  @Test
  @DisplayName("When APPEND should append data without wiping table")
  public void destSyncModeAppendTest() throws Exception {

    var sqlOp = new RedshiftSqlOperations();
    sqlOp.createTableIfNotExists(redshiftDb, SCHEMA_NAME, RAW_TABLE_NAME);
    sqlOp.insertRecords(redshiftDb, List.of(getAirbyteRecordMessage()).stream(), SCHEMA_NAME, RAW_TABLE_NAME);

    var copier = new RedshiftCopier(TEST_BUCKET, RUN_FOLDER, DestinationSyncMode.APPEND, SCHEMA_NAME, STREAM_NAME, s3Client, redshiftDb, S3_KEY_ID,
        S3_KEY, S3_REGION);

    AirbyteRecordMessage msg = getAirbyteRecordMessage();

    copier.uploadToS3(msg);
    RedshiftCopier.closeAsOneTransaction(List.of(copier), false, redshiftDb);

    assertFalse(s3Client.doesObjectExist(TEST_BUCKET, RUN_FOLDER + "/" + STREAM_NAME));

    var recordList = redshiftDb.bufferedResultSetQuery(
        connection -> {
          final String sql = "SELECT * FROM " + RAW_TABLE_NAME + ";";
          return connection.prepareStatement(sql).executeQuery();
        },
        JdbcUtils::rowToJson);

    assertEquals(2, recordList.size());
  }

  @Test
  @DisplayName("When APPEND_DEDUP should append data without wiping table")
  public void destSyncModeAppendDedupTest() throws Exception {

    var sqlOp = new RedshiftSqlOperations();
    sqlOp.createTableIfNotExists(redshiftDb, SCHEMA_NAME, RAW_TABLE_NAME);
    sqlOp.insertRecords(redshiftDb, List.of(getAirbyteRecordMessage()).stream(), SCHEMA_NAME, RAW_TABLE_NAME);

    var copier =
        new RedshiftCopier(TEST_BUCKET, RUN_FOLDER, DestinationSyncMode.APPEND_DEDUP, SCHEMA_NAME, STREAM_NAME, s3Client, redshiftDb, S3_KEY_ID,
            S3_KEY, S3_REGION);

    AirbyteRecordMessage msg = getAirbyteRecordMessage();

    copier.uploadToS3(msg);
    RedshiftCopier.closeAsOneTransaction(List.of(copier), false, redshiftDb);

    assertFalse(s3Client.doesObjectExist(TEST_BUCKET, RUN_FOLDER + "/" + STREAM_NAME));

    var recordList = redshiftDb.bufferedResultSetQuery(
        connection -> {
          final String sql = "SELECT * FROM " + RAW_TABLE_NAME + ";";
          return connection.prepareStatement(sql).executeQuery();
        },
        JdbcUtils::rowToJson);

    assertEquals(2, recordList.size());
  }

  @Test
  public void send100KTest() throws Exception {
    var now = System.currentTimeMillis();
    var copier = new RedshiftCopier(TEST_BUCKET, RUN_FOLDER, DestinationSyncMode.OVERWRITE, SCHEMA_NAME, STREAM_NAME, s3Client, redshiftDb, S3_KEY_ID,
        S3_KEY, S3_REGION);

    for (int i = 0; i < 100_000; i++) {
      var msg = getAirbyteRecordMessage();
      copier.uploadToS3(msg);
    }
    RedshiftCopier.closeAsOneTransaction(List.of(copier), false, redshiftDb);
    var duration = System.currentTimeMillis() - now;

    assertFalse(s3Client.doesObjectExist(TEST_BUCKET, RUN_FOLDER + "/" + STREAM_NAME));
    var recordList = redshiftDb.bufferedResultSetQuery(
        connection -> {
          final String sql = "SELECT * FROM " + RAW_TABLE_NAME + ";";
          return connection.prepareStatement(sql).executeQuery();
        },
        JdbcUtils::rowToJson);

    assertEquals(100_000, recordList.size());
    assertTrue(duration < 40_000); // on a 15-inch Macbook Pro 2017
  }

  @Test
  public void send1MTest() throws Exception {
    var now = System.currentTimeMillis();
    var copier = new RedshiftCopier(TEST_BUCKET, RUN_FOLDER, DestinationSyncMode.OVERWRITE, SCHEMA_NAME, STREAM_NAME, s3Client, redshiftDb, S3_KEY_ID,
        S3_KEY, S3_REGION);

    for (int i = 0; i < 1_000_000; i++) {
      var msg = getAirbyteRecordMessage();
      copier.uploadToS3(msg);
    }
    RedshiftCopier.closeAsOneTransaction(List.of(copier), false, redshiftDb);
    var duration = System.currentTimeMillis() - now;

    assertFalse(s3Client.doesObjectExist(TEST_BUCKET, RUN_FOLDER + "/" + STREAM_NAME));
    var recordList = redshiftDb.bufferedResultSetQuery(
        connection -> {
          final String sql = "SELECT * FROM " + RAW_TABLE_NAME + ";";
          return connection.prepareStatement(sql).executeQuery();
        },
        JdbcUtils::rowToJson);

    assertEquals(1000_000, recordList.size());
    assertTrue(duration < 60_000); // on a 15-inch Macbook Pro 2017
  }

  private AirbyteRecordMessage getAirbyteRecordMessage() {
    var data = mapper.createObjectNode();
    data.put("field1", "testValue");
    data.put("field2", "testValue");
    data.put("field3", "testValue");

    var msg = new AirbyteRecordMessage();
    msg.setStream(STREAM_NAME);
    msg.setData(data);
    msg.setEmittedAt(System.currentTimeMillis());
    return msg;
  }

}
