package io.airbyte.integrations.base;

/**
 * Encapsulates the connection configuration for an ssh tunnel port forward through a proxy/bastion host plus
 * the remote host and remote port to forward to a specified local port.
 */
public class SSHTunnelConfig {

  private final String method;
  private final String host;
  private final String tunnel_ssh_port;
  private final String destinationPort;
  private final String user;
  private final String sshkey;
  private final String password;

  public SSHTunnelConfig(String method, String host, String tunnel_ssh_port, String destinationPort, String user, String sshkey, String password) {
    this.method = method;
    this.host = host;
    this.destinationPort = destinationPort;
    this.tunnel_ssh_port = tunnel_ssh_port;
    this.user = user;
    this.sshkey = sshkey;
    this.password = password;
  }

  public String getMethod() {
    return method;
  }

  public String getHost() {
    return host;
  }

  public String getTunnel_ssh_port() {
    return tunnel_ssh_port;
  }

  public String getDestinationPort() {
    return destinationPort;
  }

  public String getUser() {
    return user;
  }

  // TODO: Determine if we can lock down the access on credentials a bit tighter
  public String getSSHKey() {
    return sshkey;
  }

  public String getPassword() {
    return password;
  }
}
