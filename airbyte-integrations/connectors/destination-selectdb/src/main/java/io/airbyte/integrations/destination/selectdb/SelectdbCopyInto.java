/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.destination.selectdb.exception.CopyIntoException;
import io.airbyte.integrations.destination.selectdb.exception.UploadException;
import io.airbyte.integrations.destination.selectdb.http.HttpPostBuilder;
import io.airbyte.integrations.destination.selectdb.http.HttpPutBuilder;
import io.airbyte.integrations.destination.selectdb.utils.ResponseUtils;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.*;
import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.entity.ByteArrayEntity;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SelectdbCopyInto {

  private static final Logger LOGGER = LoggerFactory.getLogger(SelectdbCopyInto.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private static final String UPLOAD_URL_PATTERN = "http://%s/copy/upload";
  private static final String COPY_URL_PATTERN = "http://%s/copy/query";
  public static final Character CSV_COLUMN_SEPARATOR = '\t';

  private final String tableName;
  private final String db;
  private final String clusterName;
  private final String loadUrl;
  private final String uploadUrlStr;
  private final String jdbcUrlStr;
  private final String user;
  private final String passwd;
  private final Integer maxRetry;
  private Boolean isUpload = false;
  private final Path path;
  private final CloseableHttpClient httpClient;

  private static final int SUCCESS = 0;
  private static final String FAIL = "1";

  private final static String COPY_SYNC = "copy.async";
  private String COPY_INTO_SQL = "";
  private String internalSatgeFileName = "";
  private Properties copyIntoSqlProp;

  public SelectdbCopyInto(
                          Path path,
                          SelectdbConnectionOptions selectdbOptions,
                          LabelInfo labelInfo,
                          CloseableHttpClient httpClient,
                          String... head) {
    this.loadUrl = selectdbOptions.getLoadUrl();
    this.db = selectdbOptions.getDb();
    this.tableName = selectdbOptions.getTable();
    this.clusterName = selectdbOptions.getClusterName();
    this.user = selectdbOptions.getUser();
    this.passwd = selectdbOptions.getPwd();
    this.uploadUrlStr = String.format(UPLOAD_URL_PATTERN, loadUrl);
    this.jdbcUrlStr = String.format(COPY_URL_PATTERN, loadUrl);
    this.copyIntoSqlProp = new Properties();
    this.maxRetry = 3;
    this.path = path;
    this.httpClient = httpClient;

    this.internalSatgeFileName = labelInfo.label() + ".csv";
    List<String> files = new ArrayList<>();
    files.add(this.internalSatgeFileName);
    this.COPY_INTO_SQL = buildCopyIntoSql(files);
  }

  public void firstCommit() throws IOException {
    Path pathChecked = Preconditions.checkNotNull(path, "upload temp CSV file is empty.");
    String uploadAddress = getUploadAddress();
    LOGGER.info("redirect to s3 address:{}", uploadAddress);
    try {
      HttpPutBuilder putBuilder = new HttpPutBuilder();
      putBuilder.setUrl(uploadAddress)
          .setCommonHeader()
          .setEntity(new ByteArrayEntity(new FileInputStream(pathChecked.toFile()).readAllBytes()));

      CloseableHttpResponse execute = httpClient.execute(putBuilder.build());
      handlePreCommitResponse(execute);
    } catch (Exception e) {
      throw new UploadException(e);
    }
    this.isUpload = true;
  }

  private String getUploadAddress() throws IOException {
    HttpPutBuilder putBuilder = new HttpPutBuilder();
    putBuilder.setUrl(uploadUrlStr)
        .setFileName(this.internalSatgeFileName)
        .setCommonHeader()
        .setEmptyEntity()
        .baseAuth(user, passwd);

    try (CloseableHttpResponse execute = httpClient.execute(putBuilder.build())) {
      int statusCode = execute.getStatusLine().getStatusCode();
      String reason = execute.getStatusLine().getReasonPhrase();
      if (statusCode == 307) {
        Header location = execute.getFirstHeader("location");
        return location.getValue();
      } else {
        HttpEntity entity = execute.getEntity();
        String result = entity == null ? null : EntityUtils.toString(entity);
        LOGGER.error("Failed get the redirected address, status {}, reason {}, response {}", statusCode, reason,
            result);
        throw new RuntimeException("Could not get the redirected address.");
      }
    }
  }

  public Boolean isUpload() {
    return this.isUpload;
  }

  private String buildCopyIntoSql(List<String> fileList) {
    StringBuilder sb = new StringBuilder();
    sb.append("COPY INTO `")
        .append(db)
        .append("`.`")
        .append(tableName)
        .append("` FROM @~('{").append(String.join(",", fileList)).append("}') ")
        .append("PROPERTIES (");

    // this copy into is sync
    copyIntoSqlProp.put(COPY_SYNC, false);
    StringJoiner props = new StringJoiner(",");
    for (Map.Entry<Object, Object> entry : copyIntoSqlProp.entrySet()) {
      String key = String.valueOf(entry.getKey());
      String value = String.valueOf(entry.getValue());
      String prop = String.format("'%s'='%s'", key, value);
      props.add(prop);
    }
    sb.append(props).append(")");
    return sb.toString();
  }

  // copy into
  public void commitTransaction() throws IOException {
    long start = System.currentTimeMillis();
    LOGGER.info("commit copy SQL: {}", COPY_INTO_SQL);
    int statusCode = -1;
    String reasonPhrase = null;
    int retry = 0;
    Map<String, String> params = new HashMap<>();
    // params.put("cluster", clusterName);
    params.put("sql", COPY_INTO_SQL);
    boolean success = false;
    CloseableHttpResponse response = null;
    String loadResult = "";
    while (retry++ <= maxRetry) {
      HttpPostBuilder postBuilder = new HttpPostBuilder();
      postBuilder.setUrl(jdbcUrlStr)
          .baseAuth(user, passwd)
          .setEntity(new StringEntity(OBJECT_MAPPER.writeValueAsString(params)));
      try {
        response = httpClient.execute(postBuilder.build());
      } catch (IOException e) {
        LOGGER.error("commit error : ", e);
        continue;
      }
      statusCode = response.getStatusLine().getStatusCode();
      reasonPhrase = response.getStatusLine().getReasonPhrase();
      if (statusCode != 200) {
        LOGGER.warn("commit failed with status {} {}, reason {}", statusCode, loadUrl, reasonPhrase);
        continue;
      } else if (response.getEntity() != null) {
        loadResult = EntityUtils.toString(response.getEntity());
        success = handleCommitResponse(loadResult);
        if (success) {
          LOGGER.info("commit success cost {}ms, response is {}", System.currentTimeMillis() - start,
              loadResult);
          break;
        } else {
          LOGGER.warn("commit failed, retry again");
        }
      }
    }

    if (!success) {
      LOGGER.error("commit error with status {}, reason {}, response {}", statusCode, reasonPhrase, loadResult);
      throw new CopyIntoException("commit error with " + COPY_INTO_SQL);
    }
  }

  public void handlePreCommitResponse(CloseableHttpResponse response) throws IOException {
    try {
      final int statusCode = response.getStatusLine().getStatusCode();
      if (statusCode == 200 && response.getEntity() != null) {
        String loadResult = EntityUtils.toString(response.getEntity());
        if (loadResult == null || loadResult.isBlank()) {
          return;
        }
        LOGGER.info("response result {}", loadResult);
        BaseResponse<HashMap<String, String>> baseResponse = new ObjectMapper().readValue(loadResult,
            new TypeReference<BaseResponse<HashMap<String, String>>>() {});
        if (baseResponse.getCode() == 0) {
          return;
        } else {
          throw new RuntimeException("upload file error: " + baseResponse.getMsg());
        }
      }
      throw new RuntimeException("upload file error: " + response.getStatusLine().toString());
    } finally {
      if (response != null) {
        response.close();
      }
    }
  }

  public boolean handleCommitResponse(String loadResult) throws IOException {
    BaseResponse<CopyIntoResp> baseResponse = OBJECT_MAPPER.readValue(loadResult,
        new TypeReference<BaseResponse<CopyIntoResp>>() {});
    if (baseResponse.getCode() == SUCCESS) {
      CopyIntoResp dataResp = baseResponse.getData();
      if (FAIL.equals(dataResp.getDataCode())) {
        LOGGER.error("copy into execute failed, reason:{}", loadResult);
        return false;
      } else {
        Map<String, String> result = dataResp.getResult();
        if (!result.get("state").equals("FINISHED") && !ResponseUtils.isCommitted(result.get("msg"))) {
          LOGGER.error("copy into load failed, reason:{}", loadResult);
          return false;
        } else {
          return true;
        }
      }
    } else {
      LOGGER.error("commit failed, reason:{}", loadResult);
      return false;
    }
  }

  public Path getPath() {
    return path;
  }

  public void close() throws IOException {
    if (null != httpClient) {
      try {
        httpClient.close();
      } catch (IOException e) {
        throw new IOException("Closing httpClient failed.", e);
      }
    }
  }

}
