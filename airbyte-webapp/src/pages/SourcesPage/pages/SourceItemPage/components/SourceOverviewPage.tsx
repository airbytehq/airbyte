import { useMemo } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { TableItemTitle } from "components/ConnectorBlocks";
import Placeholder, { ResourceTypes } from "components/Placeholder";
import { DropdownMenuOptionType } from "components/ui/DropdownMenu";

import { SourceRead } from "core/request/AirbyteClient";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useDestinationList } from "hooks/services/useDestinationHook";
import { RoutePaths } from "pages/routePaths";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import SourceConnectionTable from "./SourceConnectionTable";

const SourceOverviewPage = () => {
  const { source } = useOutletContext<{ source: SourceRead }>();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  // We load only connections attached to this source to be shown in the connections grid
  const { connections } = useConnectionList({ sourceId: [source.sourceId] });
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
    const path = `../${RoutePaths.ConnectionNew}`;
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

export default SourceOverviewPage;
