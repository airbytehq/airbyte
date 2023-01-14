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
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";

export const DestinationOverviewPage = () => {
  const params = useParams() as { "*": StepsTypes | ""; id: string };
  const { sources } = useSourceList();
  const navigate = useNavigate();
  const destination = useGetDestination(params.id);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);
  const { connections } = useConnectionList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const connectionsWithDestination = connections.filter(
    (connectionItem) => connectionItem.destinationId === destination.destinationId
  );

  const sourceDropdownOptions: DropdownMenuOptionType[] = useMemo(
    () =>
      sources.map((item) => {
        const sourceDef = sourceDefinitions.find((sd) => sd.sourceDefinitionId === item.sourceDefinitionId);
        return {
          as: "button",
          icon: <ConnectorIcon icon={sourceDef?.icon} />,
          iconPosition: "right",
          displayName: item.name,
          value: item.sourceId,
        };
      }),
    [sources, sourceDefinitions]
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
        entityIcon={destinationDefinition.icon ? getIcon(destinationDefinition.icon) : null}
        releaseStage={destinationDefinition.releaseStage}
      />
      {connectionsWithDestination.length ? (
        <DestinationConnectionTable connections={connectionsWithDestination} />
      ) : (
        <Placeholder resource={ResourceTypes.Sources} />
      )}
    </>
  );
};
