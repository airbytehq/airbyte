/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base.ssh;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.config.AirbyteSourceConfigBuilder;
import io.airbyte.cdk.integrations.config.AirbyteSourceConfig;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.string.Strings;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import org.apache.sshd.common.util.net.SshdSocketAddress;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SshTunnelForSource extends SshTunnel<AirbyteSourceConfig> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SshTunnelForDestination.class);

  public SshTunnelForSource(final AirbyteSourceConfig config,
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

  public AirbyteSourceConfig getOriginalConfig() {
    return config;
  }

  public AirbyteSourceConfig getConfigInTunnel() throws Exception {
    if (tunnelMethod.equals(TunnelMethod.NO_TUNNEL)) {
      return getOriginalConfig();
    } else {
      final AirbyteSourceConfigBuilder clone = config.cloneBuilder();
      if (hostKey != null) {
        clone.replaceNestedString(hostKey, SshdSocketAddress.LOCALHOST_ADDRESS.getHostName());
      }
      if (portKey != null) {
        clone.replaceNestedInt(portKey, tunnelLocalPort);
      }
      if (endPointKey != null) {
        final URL tunnelEndPointURL =
            new URL(remoteServiceProtocol, SshdSocketAddress.LOCALHOST_ADDRESS.getHostName(), tunnelLocalPort, remoteServicePath);
        clone.replaceNestedString(Arrays.asList(endPointKey), tunnelEndPointURL.toString());
      }
      return clone.build();
    }
  }

  public static SshTunnelForSource getInstance(final AirbyteSourceConfig config, final List<String> hostKey, final List<String> portKey) {
    Optional<JsonNode> tunnelMethodJsonConfig = config.getOptional("tunnel_method", "tunnel_method");
    final TunnelMethod tunnelMethod = tunnelMethodJsonConfig
        .map(method -> TunnelMethod.valueOf(method.asText().trim()))
        .orElse(TunnelMethod.NO_TUNNEL);
    LOGGER.info("Starting connection with method: {}", tunnelMethod);

    return new SshTunnelForSource(
        config,
        hostKey,
        portKey,
        null,
        null,
        tunnelMethod,
        Strings.safeTrim(config.getStringOrNull("tunnel_method", "tunnel_host")),
        config.getIntOrZero("tunnel_method", "tunnel_port"),
        Strings.safeTrim(config.getStringOrNull("tunnel_method", "tunnel_user")),
        Strings.safeTrim(config.getStringOrNull("tunnel_method", "ssh_key")),
        Strings.safeTrim(config.getStringOrNull("tunnel_method", "tunnel_user_password")),
        Strings.safeTrim(config.getStringOrNull(hostKey)),
        config.getIntOrZero(portKey));
  }

  public static <T> T sshWrap(final AirbyteSourceConfig config,
                              final List<String> hostKey,
                              final List<String> portKey,
                              final CheckedFunction<AirbyteSourceConfig, T, Exception> wrapped)
      throws Exception {
    try (final SshTunnelForSource sshTunnel = SshTunnelForSource.getInstance(config, hostKey, portKey)) {
      return wrapped.apply(sshTunnel.getConfigInTunnel());
    }
  }

}
