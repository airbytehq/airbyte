/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import org.apache.sshd.common.util.net.SshdSocketAddress;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SshTunnelForDestination extends SshTunnel<JsonNode> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SshTunnelForDestination.class);

  public SshTunnelForDestination(final JsonNode config,
                                 final List<String> hostKey,
                                 final List<String> portKey,
                                 final String endPointKey,
                                 final String remoteServiceUrl,
                                 final TunnelMethod tunnelMethod,
                                 final String tunnelHost,
                                 final int tunnelPort,
                                 final String tunnelUser,
                                 final String sshKey,
                                 final String tunnelUserPassword,
                                 final String remoteServiceHost,
                                 final int remoteServicePort) {
    super(config, hostKey, portKey, endPointKey, remoteServiceUrl, tunnelMethod, tunnelHost, tunnelPort, tunnelUser, sshKey, tunnelUserPassword,
        remoteServiceHost, remoteServicePort);

  }

  public JsonNode getConfigInTunnel() throws Exception {
    if (tunnelMethod.equals(TunnelMethod.NO_TUNNEL)) {
      return getOriginalConfig();
    } else {
      final JsonNode clone = Jsons.clone(config);
      if (hostKey != null) {
        Jsons.replaceNestedString(clone, hostKey, SshdSocketAddress.LOCALHOST_ADDRESS.getHostName());
      }
      if (portKey != null) {
        Jsons.replaceNestedInt(clone, portKey, tunnelLocalPort);
      }
      if (endPointKey != null) {
        final URL tunnelEndPointURL =
            new URL(remoteServiceProtocol, SshdSocketAddress.LOCALHOST_ADDRESS.getHostName(), tunnelLocalPort, remoteServicePath);
        Jsons.replaceNestedString(clone, Arrays.asList(endPointKey), tunnelEndPointURL.toString());
      }
      return clone;
    }
  }

  public static SshTunnelForDestination getInstance(final JsonNode config, final List<String> hostKey, final List<String> portKey) {
    final TunnelMethod tunnelMethod = Jsons.getOptional(config, "tunnel_method", "tunnel_method")
        .map(method -> TunnelMethod.valueOf(method.asText().trim()))
        .orElse(TunnelMethod.NO_TUNNEL);
    LOGGER.info("Starting connection with method: {}", tunnelMethod);

    return new SshTunnelForDestination(
        config,
        hostKey,
        portKey,
        null,
        null,
        tunnelMethod,
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_host")),
        Jsons.getIntOrZero(config, "tunnel_method", "tunnel_port"),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "ssh_key")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user_password")),
        Strings.safeTrim(Jsons.getStringOrNull(config, hostKey)),
        Jsons.getIntOrZero(config, portKey));
  }

  public static SshTunnelForDestination getInstance(final JsonNode config, final String endPointKey) throws Exception {
    final TunnelMethod tunnelMethod = Jsons.getOptional(config, "tunnel_method", "tunnel_method")
        .map(method -> TunnelMethod.valueOf(method.asText().trim()))
        .orElse(TunnelMethod.NO_TUNNEL);
    LOGGER.info("Starting connection with method: {}", tunnelMethod);

    return new SshTunnelForDestination(
        config,
        null,
        null,
        endPointKey,
        Jsons.getStringOrNull(config, endPointKey),
        tunnelMethod,
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_host")),
        Jsons.getIntOrZero(config, "tunnel_method", "tunnel_port"),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "ssh_key")),
        Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user_password")),
        null, 0);
  }

  public static <T> T sshWrap(final JsonNode config,
                              final List<String> hostKey,
                              final List<String> portKey,
                              final CheckedFunction<JsonNode, T, Exception> wrapped)
      throws Exception {
    try (final SshTunnelForDestination sshTunnel = SshTunnelForDestination.getInstance(config, hostKey, portKey)) {
      return wrapped.apply(sshTunnel.getConfigInTunnel());
    }
  }

  public static <T> T sshWrap(final JsonNode config,
                              final String endPointKey,
                              final CheckedFunction<JsonNode, T, Exception> wrapped)
      throws Exception {
    try (final SshTunnelForDestination sshTunnel = SshTunnelForDestination.getInstance(config, endPointKey)) {
      return wrapped.apply(sshTunnel.getConfigInTunnel());
    }
  }

}
