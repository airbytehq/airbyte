import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";

import { Block, Title, FormContent, FormContentTitle } from "./PageComponents";
import Table from "../../../components/Table";
import { CellProps } from "react-table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import config from "../../../config";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";
import DestinationResource from "../../../core/resources/Destination";

const DestinationsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const destinations = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const [feedback, setFeedback] = useState(""); // only one destination !
  // Now we have only one destination. If we support multiple destinations we will change it
  const currentDestination = destinations.destinations[0];

  const updateDestinationDefinition = useFetcher(
    DestinationDefinitionResource.updateShape()
  );

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateDestinationDefinition(
          {},
          {
            destinationDefinitionId: id,
            dockerImageTag: version
          }
        );
        setFeedback("success");
      } catch (e) {
        const message =
          e.status === 422
            ? formatMessage({
                id: "form.imageCannotFound"
              })
            : formatMessage({
                id: "form.someError"
              });
        setFeedback(message);
      }
    },
    [formatMessage, updateDestinationDefinition]
  );

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="admin.connectors" />,
        accessor: "name",
        customWidth: 25,
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
        Header: (
          <FormContentTitle>
            <FormattedMessage id="admin.tag" />
          </FormContentTitle>
        ),
        accessor: "dockerImageTag",
        collapse: true,
        Cell: ({
          cell,
          row
        }: CellProps<{ destinationDefinitionId: string }>) => (
          <VersionCell
            version={cell.value}
            id={row.original.destinationDefinitionId}
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

  const destinationInfo = destinationDefinitions.find(
    // TODO change to destinationDefId when changing destinationImpl
    item =>
      item.destinationDefinitionId ===
      currentDestination.destinationDefinitionId
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
        <Table columns={columnsAllDestinations} data={destinationDefinitions} />
      </Block>
    </>
  );
};

export default DestinationsView;
