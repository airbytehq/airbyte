package io.dataline.conduit.workers.singer;

public class DiscoveryOutput {
  // TODO line this up with conduit config type
  public final String catalog;

  public DiscoveryOutput(String catalog) {
    this.catalog = catalog;
  }
}
