/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp;

import com.fasterxml.jackson.databind.JsonNode;
import com.jcraft.jsch.Channel;
import com.jcraft.jsch.ChannelSftp;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.jcraft.jsch.SftpException;
import io.airbyte.integrations.source.sftp.enums.SftpAuthMethod;
import io.airbyte.integrations.source.sftp.enums.SupportedFileExtension;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Properties;
import java.util.Vector;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SftpClient {

  protected static final Logger LOGGER = LoggerFactory.getLogger(SftpClient.class);
  private static final String CHANNEL_SFTP = "sftp";
  private static final String STRICT_HOST_KEY_CHECKING = "StrictHostKeyChecking";

  private final String username;
  private final String hostAddress;
  private final int port;
  private final SftpAuthMethod authMethod;
  private final JsonNode config;
  private final int connectionTimeoutMillis = 60000;
  private final JSch jsch;
  private Session session;
  private ChannelSftp channelSftp;

  public SftpClient(JsonNode config) {
    this.config = config;
    jsch = new JSch();
    username = config.has("user") ? config.get("user").asText() : "";
    hostAddress = config.has("host") ? config.get("host").asText() : "";
    port = config.has("port") ? config.get("port").asInt() : 22;
    authMethod = SftpAuthMethod.valueOf(config.get("credentials").get("auth_method").asText());
  }

  public void connect() {
    try {
      LOGGER.info("Connecting to the server");
      configureSession();
      configureAuthMethod();
      LOGGER.debug("Connecting to host: {} at port: {}", hostAddress, port);
      session.connect();
      Channel channel = session.openChannel(CHANNEL_SFTP);
      channel.connect();

      channelSftp = (ChannelSftp) channel;
      LOGGER.info("Connected successfully");
    } catch (Exception e) {
      LOGGER.error("Exception attempting to connect to the server:", e);
      throw new RuntimeException(e);
    }
  }

  private void configureSession() throws JSchException {
    Properties properties = new Properties();
    properties.put(STRICT_HOST_KEY_CHECKING, "no");
    session = jsch.getSession(username, hostAddress, port);
    session.setConfig(properties);
    session.setTimeout(connectionTimeoutMillis);
  }

  public void disconnect() {
    LOGGER.info("Disconnecting from the server");
    if (channelSftp != null) {
      channelSftp.disconnect();
    }
    if (session != null) {
      session.disconnect();
    }
    LOGGER.info("Disconnected successfully");
  }

  public boolean isConnected() {
    return channelSftp != null && channelSftp.isConnected();
  }

  @SuppressWarnings("rawtypes")
  public Vector lsFile(SupportedFileExtension fileExtension) {
    try {
      return channelSftp.ls("*." + fileExtension.typeName);
    } catch (SftpException e) {
      LOGGER.error("Exception occurred while trying to find files with type {} : ", fileExtension, e);
      throw new RuntimeException(e);
    }
  }

  public void changeWorkingDirectory(String path) throws SftpException {
    channelSftp.cd(path);
  }

  public ByteArrayInputStream getFile(String fileName) {
    try (InputStream inputStream = channelSftp.get(fileName)) {
      return new ByteArrayInputStream(IOUtils.toByteArray(inputStream));
    } catch (Exception e) {
      LOGGER.error("Exception occurred while trying to download file {} : ", fileName, e);
      throw new RuntimeException(e);
    }
  }

  private void configureAuthMethod() throws Exception {
    switch (authMethod) {
      case SSH_PASSWORD_AUTH -> session.setPassword(config.get("credentials").get("auth_user_password").asText());
      case SSH_KEY_AUTH -> {
        File tempFile = File.createTempFile("private_key", "", null);
        FileOutputStream fos = new FileOutputStream(tempFile);
        fos.write(config.get("credentials").get("auth_ssh_key").asText().getBytes(StandardCharsets.UTF_8));
        jsch.addIdentity(tempFile.getAbsolutePath());
      }
      default -> throw new RuntimeException("Unsupported SFTP Authentication type");
    }
  }

}
