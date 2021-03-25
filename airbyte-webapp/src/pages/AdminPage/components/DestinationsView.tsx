import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useFetcher, useResource } from "rest-hooks";
import { CellProps } from "react-table";
import { useAsyncFn } from "react-use";

import { Block, Title, FormContentTitle } from "./PageComponents";
import Table from "components/Table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import config from "config";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import { DestinationResource } from "core/resources/Destination";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import UpgradeAllButton from "./UpgradeAllButton";
import useNotification from "components/hooks/services/useNotification";

const DestinationsView: React.FC = () => {
  const [successUpdate, setSuccessUpdate] = useState(false);
  const formatMessage = useIntl().formatMessage;
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );
  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});

  const updateDestinationDefinition = useFetcher(
    DestinationDefinitionResource.updateShape()
  );

  const { hasNewDestinationVersion } = useNotification();

  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateDestinationDefinition(
          {},
          {
            destinationDefinitionId: id,
            dockerImageTag: version,
          }
        );
        setFeedbackList({ ...feedbackList, [id]: "success" });
      } catch (e) {
        const messageId =
          e.status === 422 ? "form.imageCannotFound" : "form.someError";
        setFeedbackList({
          ...feedbackList,
          [id]: formatMessage({ id: messageId }),
        });
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
        Cell: ({
          cell,
          row,
        }: CellProps<{
          latestDockerImageTag: string;
          dockerImageTag: string;
        }>) => (
          <ConnectorCell
            connectorName={cell.value}
            hasUpdate={
              row.original.latestDockerImageTag !== row.original.dockerImageTag
            }
          />
        ),
      },
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "dockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ documentationUrl: string }>) => (
          <ImageCell
            imageName={cell.value}
            link={row.original.documentationUrl}
          />
        ),
      },
      {
        Header: <FormattedMessage id="admin.currentVersion" />,
        accessor: "dockerImageTag",
        customWidth: 10,
      },
      {
        Header: (
          <FormContentTitle>
            <FormattedMessage id="admin.changeTo" />
          </FormContentTitle>
        ),
        accessor: "latestDockerImageTag",
        collapse: true,
        Cell: ({
          cell,
          row,
        }: CellProps<{
          destinationDefinitionId: string;
          dockerImageTag: string;
        }>) => (
          <VersionCell
            version={cell.value}
            id={row.original.destinationDefinitionId}
            onChange={onUpdateVersion}
            feedback={feedbackList[row.original.destinationDefinitionId]}
            currentVersion={row.original.dockerImageTag}
          />
        ),
      },
    ],
    [feedbackList, onUpdateVersion]
  );

  const usedDestinationDefinitions = useMemo<DestinationDefinition[]>(() => {
    const destinationDefinitionMap = new Map<string, DestinationDefinition>();
    destinations.forEach((destination) => {
      const destinationDefinition = destinationDefinitions.find(
        (destinationDefinition) =>
          destinationDefinition.destinationDefinitionId ===
          destination.destinationDefinitionId
      );

      if (destinationDefinition) {
        destinationDefinitionMap.set(
          destinationDefinition.destinationDefinitionId,
          destinationDefinition
        );
      }
    });

    return Array.from(destinationDefinitionMap.values());
  }, [destinations, destinationDefinitions]);

  const { updateAllDestinationVersions } = useNotification();

  const [{ loading, error }, onUpdate] = useAsyncFn(async () => {
    setSuccessUpdate(false);
    await updateAllDestinationVersions();
    setSuccessUpdate(true);
    setTimeout(() => {
      setSuccessUpdate(false);
    }, 2000);
  }, [updateAllDestinationVersions]);

  return (
    <>
      {usedDestinationDefinitions.length ? (
        <Block>
          <Title bold>
            <FormattedMessage id="admin.manageDestination" />
            {(hasNewDestinationVersion || successUpdate) && (
              <UpgradeAllButton
                isLoading={loading}
                hasError={!!error && !loading}
                hasSuccess={successUpdate}
                onUpdate={onUpdate}
              />
            )}
          </Title>
          <Table columns={columns} data={usedDestinationDefinitions} />
        </Block>
      ) : null}

      <Block>
        <Title bold>
          <FormattedMessage id="admin.availableDestinations" />
          {(hasNewDestinationVersion || successUpdate) &&
            !usedDestinationDefinitions.length && (
              <UpgradeAllButton
                isLoading={loading}
                hasError={!!error && !loading}
                hasSuccess={successUpdate}
                onUpdate={onUpdate}
              />
            )}
        </Title>
        <Table columns={columns} data={destinationDefinitions} />
      </Block>
    </>
  );
};

export default DestinationsView;
