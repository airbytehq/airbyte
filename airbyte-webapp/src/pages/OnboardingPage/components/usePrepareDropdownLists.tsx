import { useMemo } from "react";
import { useResource } from "rest-hooks";

import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";

const usePrepareDropdownLists = () => {
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {}
  );
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {}
  );

  const sourcesDropDownData = useMemo(
    () =>
      sourceDefinitions.map((item) => ({
        text: item.name,
        value: item.sourceDefinitionId,
        img: "/default-logo-catalog.svg",
      })),
    [sourceDefinitions]
  );

  const destinationsDropDownData = useMemo(
    () =>
      destinationDefinitions.map((item) => ({
        text: item.name,
        value: item.destinationDefinitionId,
        img: "/default-logo-catalog.svg",
      })),
    [destinationDefinitions]
  );

  const getSourceDefinitionById = (id: string) =>
    sourceDefinitions.find((item) => item.sourceDefinitionId === id);

  const getDestinationDefinitionById = (id: string) =>
    destinationDefinitions.find((item) => item.destinationDefinitionId === id);

  return {
    sourcesDropDownData,
    destinationsDropDownData,
    getSourceDefinitionById: getSourceDefinitionById,
    getDestinationDefinitionById,
  };
};

export default usePrepareDropdownLists;
