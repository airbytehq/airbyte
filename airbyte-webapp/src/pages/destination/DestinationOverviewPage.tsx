import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { StepsTypes, TableItemTitle } from "components/ConnectorBlocks";
import { DestinationConnectionTable } from "components/destination/DestinationConnectionTable";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { DropdownMenuOptionType } from "components/ui/DropdownMenu";

import { useConnectionList } from "hooks/services/useConnectionHook";
import { useGetDestination } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";
import { DestinationPaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";

export const DestinationOverviewPage = () => {
  const params = useParams() as { "*": StepsTypes | ""; id: string };
  const navigate = useNavigate();

  const destination = useGetDestination(params.id);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);
  // We load only connections attached to this destination to be shown in the connections grid
  const { connections } = useConnectionList({ destinationId: [destination.destinationId] });

  // We load all sources so the add source button has a pre-filled list of options.
  const { sources } = useSourceList();
  const sourceDropdownOptions = useMemo<DropdownMenuOptionType[]>(
    () =>
      sources.map((source) => {
        return {
          as: "button",
          icon: <ConnectorIcon icon={source.icon} />,
          iconPosition: "right",
          displayName: source.name,
          value: source.sourceId,
        };
      }),
    [sources]
  );

  const onSelect = (data: DropdownMenuOptionType) => {
    const path = `../../${DestinationPaths.NewConnection}`;
    const state =
      data.value === "create-new-item"
        ? { destinationId: destination.destinationId }
        : {
            sourceId: data.value,
            destinationId: destination.destinationId,
          };

    navigate(path, { state });
  };

  return (
    <>
      <TableItemTitle
        type="source"
        dropdownOptions={sourceDropdownOptions}
        onSelect={onSelect}
        entityName={destination.name}
        entity={destination.destinationName}
        entityIcon={destination.icon}
        releaseStage={destinationDefinition.releaseStage}
      />
      {connections.length ? (
        <DestinationConnectionTable connections={connections} />
      ) : (
        <Placeholder resource={ResourceTypes.Sources} />
      )}
    </>
  );
};

export default DestinationOverviewPage;
