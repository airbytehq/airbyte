import { useQuery } from "react-query";

import { getExcludedConnectorIds } from "core/domain/connector/constants";
import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";

import availableSourceDefinitions from "./sourceDefinitions.json";

interface Catalog {
  destinations: DestinationDefinitionRead[];
  sources: SourceDefinitionRead[];
}
const fetchCatalog = async (): Promise<Catalog> => {
  const path = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/cloud_catalog.json";
  const response = await fetch(path);
  return response.json();
};

export const useGetSourceDefinitions = () => {
  return useQuery("cloud_catalog", fetchCatalog, {
    select: (data) => {
      const excludedConnectorIds = getExcludedConnectorIds();
      return data.sources
        .filter((source) => !excludedConnectorIds.includes(source.sourceDefinitionId))
        .map((source) => {
          const icon = availableSourceDefinitions.sourceDefinitions.find(
            (src) => src.sourceDefinitionId === source.sourceDefinitionId
          )?.icon;
          return {
            ...source,
            icon,
          };
        });
    },
  });
};
