import React, { useCallback, useMemo, useState } from "react";
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
import ConnectionResource from "../../../core/resources/Connection";

const DestinationsView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const [feedbackList, setFeedbackList] = useState<any>({});

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
        setFeedbackList({ ...feedbackList, [id]: "success" });
      } catch (e) {
        const message =
          e.status === 422
            ? formatMessage({
                id: "form.imageCannotFound"
              })
            : formatMessage({
                id: "form.someError"
              });
        setFeedbackList({ ...feedbackList, [id]: message });
      }
    },
    [feedbackList, formatMessage, updateDestinationDefinition]
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
            feedback={feedbackList[row.original.destinationDefinitionId]}
          />
        )
      }
    ],
    [columns, feedbackList, onUpdateVersion]
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

  const usedDestination = useMemo(() => {
    const allDestination = connections.map(item => {
      const destinationInfo = destinationDefinitions.find(
        destination =>
          destination.destinationDefinitionId ===
          item.destination?.destinationDefinitionId
      );
      return {
        name: item.destination?.destinationName,
        destinationDefinitionId:
          item.destination?.destinationDefinitionId || "",
        dockerRepository: destinationInfo?.dockerRepository,
        dockerImageTag: destinationInfo?.dockerImageTag,
        documentationUrl: destinationInfo?.documentationUrl,
        feedback: ""
      };
    });

    const uniqDestination = allDestination.reduce(
      (map, item) => ({ ...map, [item.destinationDefinitionId]: item }),
      {}
    );

    return Object.values(uniqDestination);
  }, [connections, destinationDefinitions]);

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
          <FormattedMessage id="admin.availableDestinations" />
        </Title>
        <Table columns={columnsAllDestinations} data={destinationDefinitions} />
      </Block>
    </>
  );
};

export default DestinationsView;
