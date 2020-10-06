import React from "react";
import { FormattedMessage } from "react-intl";

import { Block, Title } from "./PageComponents";
import Table from "../../../components/Table";
import { CellProps } from "react-table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import { useResource } from "rest-hooks/lib/react-integration/hooks";
import config from "../../../config";
import DestinationResource from "../../../core/resources/Destination";
import DestinationImplementationResource from "../../../core/resources/DestinationImplementation";

const DestinationsView: React.FC = () => {
  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const destinationsImplementation = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );

  // Now we have only one destination. If we support multiple destinations we will change it
  const currentDestination = destinationsImplementation.destinations[0];

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="admin.connectors" />,
        accessor: "name",
        customWidth: 34,
        Cell: ({ cell }: CellProps<{}>) => (
          <ConnectorCell connectorName={cell.value} />
        )
      }
    ],
    []
  );
  const columnsCurrentDestination = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.codeSource" />,
        accessor: "defaultDockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ imageLink: string }>) => (
          <ImageCell imageName={cell.value} link={row.original.imageLink} />
        )
      },
      {
        Header: <FormattedMessage id="admin.version" />,
        accessor: "defaultDockerImageVersion",
        collapse: true,
        Cell: ({ cell }: CellProps<{}>) => <VersionCell version={cell.value} />
      }
    ],
    [columns]
  );

  const columnsAllDestinations = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "defaultDockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ imageLink: string }>) => (
          <ImageCell imageName={cell.value} link={row.original.imageLink} />
        )
      },
      {
        Header: "",
        accessor: "defaultDockerImageVersion",
        collapse: true,
        Cell: () => <VersionCell empty />
      }
    ],
    [columns]
  );

  const destinationInfo = destinations.find(
    item => item.destinationId === currentDestination.destinationId
  );

  const usedDestination = destinationInfo ? [destinationInfo] : [];

  return (
    <>
      <Block>
        <Title bold>
          <FormattedMessage id="admin.manageDestination" />
        </Title>
        <Table columns={columnsCurrentDestination} data={usedDestination} />
      </Block>

      <Block>
        <Title bold>
          <FormattedMessage id="admin.supportMultipleDestinations" />
        </Title>
        <Table columns={columnsAllDestinations} data={destinations} />
      </Block>
    </>
  );
};

export default DestinationsView;
