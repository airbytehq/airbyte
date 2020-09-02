import { useMemo } from "react";
import { useResource } from "rest-hooks";

import SourceResource from "../../../core/resources/Source";
import DestinationResource from "../../../core/resources/Destination";

const PrepareDropDownLists = () => {
  const { sources } = useResource(SourceResource.listShape(), {});
  const { destinations } = useResource(DestinationResource.listShape(), {});

  const sourcesDropDownData = useMemo(
    () =>
      sources.map(item => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg"
      })),
    [sources]
  );

  const destinationsDropDownData = useMemo(
    () =>
      destinations.map(item => ({
        text: item.name,
        value: item.destinationId,
        img: "/default-logo-catalog.svg"
      })),
    [destinations]
  );

  return {
    sourcesDropDownData,
    destinationsDropDownData
  };
};

export default PrepareDropDownLists;
