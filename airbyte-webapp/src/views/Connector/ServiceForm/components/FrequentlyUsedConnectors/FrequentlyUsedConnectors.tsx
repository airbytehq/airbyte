import React, { useMemo } from "react";

import { ConnectorDefinition } from "core/domain/connector";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { useExperiment } from "hooks/services/Experiment";
import { useClearbitReveal } from "hooks/services/useClearbitReveal";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { clearbitRevealSourceIds } from "packages/cloud/experiments/ClearbitRevealSources";

import { FrequentlyUsedConnectorsCard } from "./FrequentlyUsedConnectorsCard";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { getSortedFrequentlyUsedDataUsingExperiment } from "./utils";

interface FrequentlyUsedConnectorsProps {
  connectorType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  onConnectorClick: (id: string) => void;
}

const defaultFrequentlyUsedSourceIds = ["71607ba1-c0ac-4799-8049-7f4b90dd50f7", "36c891d9-4bd9-43ac-bad2-10e12756272c"];

const defaultFrequentlyUsedDestinationIds = [
  "22f6c74f-5699-40ff-833c-4a879ea40133",
  "424892c4-daac-4491-b35d-c6688ba547ba",
];

export const FrequentlyUsedConnectors: React.FC<FrequentlyUsedConnectorsProps> = ({
  connectorType,
  availableServices,
  onConnectorClick,
}) => {
  const reveal = useClearbitReveal();
  const workspace = useCurrentWorkspace();
  const frequentlyUsedDestinationIds = useExperiment(
    "connector.frequentlyUsedDestinationIds",
    defaultFrequentlyUsedDestinationIds
  );
  const revealSort = useExperiment("connector.revealSort", false);
  const frequentlyUsedConnectors = {
    source: revealSort && reveal ? clearbitRevealSourceIds(reveal.company.tech) : defaultFrequentlyUsedSourceIds,
    destination: frequentlyUsedDestinationIds,
  };
  const frequentlyUsedConnectorIds = frequentlyUsedConnectors[connectorType];
  console.log(frequentlyUsedConnectorIds);

  const { trackSelectedSuggestedConnector } = useAnalyticsTrackFunctions(connectorType);

  const availableConnectorDefinitions = useAvailableConnectorDefinitions(availableServices, workspace);
  const sortedFrequentlyUsedData = useMemo(
    () => getSortedFrequentlyUsedDataUsingExperiment(availableConnectorDefinitions, frequentlyUsedConnectorIds),
    [availableConnectorDefinitions, frequentlyUsedConnectorIds]
  );

  const onFrequentlyUsedConnectorCardClick = (id: string, connectorName: string) => {
    onConnectorClick(id);
    trackSelectedSuggestedConnector(id, connectorName);
  };

  return (
    <FrequentlyUsedConnectorsCard
      connectorType={connectorType}
      connectors={sortedFrequentlyUsedData}
      onClick={onFrequentlyUsedConnectorCardClick}
    />
  );
};
