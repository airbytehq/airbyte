import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { CellProps } from "react-table";
import { useFetcher, useResource } from "rest-hooks";

import Table from "components/Table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import config from "config";
import { Block, FormContentTitle, Title } from "./PageComponents";
import SourceDefinitionResource, {
  SourceDefinition,
} from "core/resources/SourceDefinition";
import { SourceResource } from "core/resources/Source";

const SourcesView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );

  const updateSourceDefinition = useFetcher(
    SourceDefinitionResource.updateShape()
  );

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});
  const onUpdateVersion = useCallback(
    async ({ id, version }: { id: string; version: string }) => {
      try {
        await updateSourceDefinition(
          {},
          {
            sourceDefinitionId: id,
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
    [feedbackList, formatMessage, updateSourceDefinition]
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
          sourceDefinitionId: string;
          dockerImageTag: string;
        }>) => (
          <VersionCell
            version={cell.value}
            id={row.original.sourceDefinitionId}
            onChange={onUpdateVersion}
            feedback={feedbackList[row.original.sourceDefinitionId]}
            currentVersion={row.original.dockerImageTag}
          />
        ),
      },
    ],
    [feedbackList, onUpdateVersion]
  );

  const usedSourcesDefinitions = useMemo<SourceDefinition[]>(() => {
    const sourceDefinitionMap = new Map<string, SourceDefinition>();
    sources.forEach((source) => {
      const sourceDestination = sourceDefinitions.find(
        (sourceDefinition) =>
          sourceDefinition.sourceDefinitionId === source.sourceDefinitionId
      );

      if (sourceDestination) {
        sourceDefinitionMap.set(source?.sourceDefinitionId, sourceDestination);
      }
    });

    return Array.from(sourceDefinitionMap.values());
  }, [sources, sourceDefinitions]);

  return (
    <>
      {usedSourcesDefinitions.length ? (
        <Block>
          <Title bold>
            <FormattedMessage id="admin.manageSource" />
          </Title>
          <Table columns={columns} data={usedSourcesDefinitions} />
        </Block>
      ) : null}

      <Block>
        <Title bold>
          <FormattedMessage id="admin.availableSource" />
        </Title>
        <Table columns={columns} data={sourceDefinitions} />
      </Block>
    </>
  );
};

export default SourcesView;
