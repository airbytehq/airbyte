const getConnectorsBySupportLevel = (connectors, registry) => {
  const connectorsWithSupportLevel = connectors.map((item) => {
    const connector = registry.find(
      (connector) =>
        connector.documentationUrl_cloud?.includes(item.docId) ||
        connector.documentationUrl_oss?.includes(item.docId)
    );

    if (connector) {
      return {
        ...item,
        customProps: {
          supportLevel:
            connector.supportLevel_cloud || connector.supportLevel_oss,
        },
      };
    }

    return item;
  });
  const groupedConnectors = connectorsWithSupportLevel.reduce((acc, item) => {
    const supportLevel = item.customProps?.supportLevel || "community";
    if (!acc[supportLevel]) {
      acc[supportLevel] = [];
    }
    acc[supportLevel].push(item);
    return acc;
  }, {});

  return Object.entries(groupedConnectors)
    .sort((a, b) => {
      const supportLevelA = a[0];
      const supportLevelB = b[0];
      return supportLevelA.localeCompare(supportLevelB);
    })
    .map(([supportLevel, items]) => {
      return {
        type: "category",
        collapsible: true,
        collapsed: true,
        label:
          supportLevel === "certified" ? "Airbyte Connectors" : "Marketplace",
        items: items,
      };
    });
};

export { getConnectorsBySupportLevel };
