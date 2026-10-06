const DATA_WORKER_CPU_DIVISOR = 8;

const DEFAULT_SYNC_RESOURCE_PROFILES_BY_SOURCE_TYPE = {
  api: {
    source: 0.8,
    destination: 0.3,
    orchestrator: 0.3,
    displayPrecision: 1,
  },
  database: {
    source: 1,
    destination: 1,
    orchestrator: 2,
    displayPrecision: 2,
  },
  default: {
    source: 0.8,
    destination: 0.3,
    orchestrator: 0.3,
    displayPrecision: 1,
  },
  file: {
    source: 0.8,
    destination: 0.3,
    orchestrator: 0.3,
    displayPrecision: 1,
  },
  custom: {
    source: 0.8,
    destination: 0.3,
    orchestrator: 0.3,
    displayPrecision: 1,
  },
};

const DEFAULT_DISPLAY_VALUES_BY_SOURCE_TYPE = Object.fromEntries(
  Object.entries(DEFAULT_SYNC_RESOURCE_PROFILES_BY_SOURCE_TYPE).map(
    ([sourceType, resourceProfile]) => [
      sourceType,
      Number(
        (
          (resourceProfile.source +
            resourceProfile.destination +
            resourceProfile.orchestrator) /
          DATA_WORKER_CPU_DIVISOR
        ).toFixed(resourceProfile.displayPrecision),
      ).toString(),
    ],
  ),
);

const getDefaultDataWorkersForSource = (registryEntry) => {
  if (registryEntry?.connector_type !== "source") {
    return;
  }

  return DEFAULT_DISPLAY_VALUES_BY_SOURCE_TYPE[registryEntry.sourceType];
};

module.exports = {
  getDefaultDataWorkersForSource,
};
