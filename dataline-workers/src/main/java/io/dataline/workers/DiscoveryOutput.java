package io.dataline.workers;

public class DiscoveryOutput {
  // TODO line this up with conduit config type
  private final String catalog;

  public DiscoveryOutput(String catalog) {
    this.catalog = catalog;
  }

  public String getCatalog() {
    return catalog;
  }
}
