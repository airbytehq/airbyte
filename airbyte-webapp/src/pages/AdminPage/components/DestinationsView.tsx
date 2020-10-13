import React, { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";

import { Block, Title, FormContent } from "./PageComponents";
import Table from "../../../components/Table";
import { CellProps } from "react-table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
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

  const [feedback, setFeedback] = useState(""); // only one destination !
  // Now we have only one destination. If we support multiple destinations we will change it
  const currentDestination = destinationsImplementation.destinations[0];

  const updateDestination = useFetcher(DestinationResource.updateShape());

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateDestination(
          {},
          {
            destinationId: id,
            dockerImageTag: version
          }
        );
        setFeedback("success");
      } catch (e) {
        setFeedback("error");
      }
    },
    [updateDestination]
  );

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
        accessor: "dockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ documentationUrl: string }>) => (
          <ImageCell
            imageName={cell.value}
            link={row.original.documentationUrl}
          />
        )
      },
      {
        Header: <FormattedMessage id="admin.version" />,
        accessor: "dockerImageTag",
        collapse: true,
        Cell: ({ cell, row }: CellProps<{ destinationId: string }>) => (
          <VersionCell
            version={cell.value}
            id={row.original.destinationId}
            onChange={onUpdateVersion}
            feedback={feedback}
          />
        )
      }
    ],
    [columns, feedback, onUpdateVersion]
  );

  const columnsAllDestinations = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "dockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ documentationUrl: string }>) => (
          <ImageCell
            imageName={cell.value}
            link={row.original.documentationUrl}
          />
        )
      },
      {
        Header: "",
        accessor: "dockerImageTag",
        collapse: true,
        Cell: () => <FormContent />
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
