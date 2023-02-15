import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { TableItemTitle } from "components/ConnectorBlocks";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { DropdownMenuOptionType } from "components/ui/DropdownMenu";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { SourcePaths } from "pages/routePaths";

import { useSourceOverviewContext } from "./sourceOverviewContext";
const SourceConnectionTable = React.lazy(() => import("./SourceConnectionTable"));

export const SourceOverviewPage = () => {
  const { source, sourceDefinition, connections } = useSourceOverviewContext();
  // We load all destinations so the add destination button has a pre-filled list of options.
  const { destinations } = useDestinationList();

  const navigate = useNavigate();

  const destinationDropdownOptions: DropdownMenuOptionType[] = useMemo(
    () =>
      destinations.map((destination) => {
        return {
          as: "button",
          icon: <ConnectorIcon icon={destination.icon} />,
          iconPosition: "right",
          displayName: destination.name,
          value: destination.destinationId,
        };
      }),
    [destinations]
  );

  const onSelect = (data: DropdownMenuOptionType) => {
    const path = `../${SourcePaths.NewConnection}`;
    const state =
      data.value === "create-new-item"
        ? { sourceId: source.sourceId }
        : {
            destinationId: data.value,
            sourceId: source.sourceId,
          };

    navigate(path, { state });
  };

  return (
    <>
      <TableItemTitle
        type="destination"
        dropdownOptions={destinationDropdownOptions}
        onSelect={onSelect}
        entity={source.sourceName}
        entityName={source.name}
        entityIcon={source.icon}
        releaseStage={sourceDefinition.releaseStage}
      />
      {connections.length ? (
        <SourceConnectionTable connections={connections} />
      ) : (
        <Placeholder resource={ResourceTypes.Destinations} />
      )}
    </>
  );
};
