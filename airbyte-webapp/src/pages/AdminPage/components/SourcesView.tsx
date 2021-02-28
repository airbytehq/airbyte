import React, { useCallback, useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { CellProps } from "react-table";
import { useFetcher, useResource } from "rest-hooks";

import Table from "components/Table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import ConnectionResource from "core/resources/Connection";
import config from "config";
import { Block, Title, FormContentTitle } from "./PageComponents";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import { Source } from "core/resources/Source";

const SourcesView: React.FC = () => {
  const formatMessage = useIntl().formatMessage;
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId,
  });

  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId,
    }
  );

  const [feedbackList, setFeedbackList] = useState<Record<string, string>>({});

  const updateSourceDefinition = useFetcher(
    SourceDefinitionResource.updateShape()
  );
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
        const message =
          e.status === 422
            ? formatMessage({
                id: "form.imageCannotFound",
              })
            : formatMessage({
                id: "form.someError",
              });
        setFeedbackList({ ...feedbackList, [id]: message });
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
        Cell: ({ cell }: CellProps<never>) => (
          <ConnectorCell connectorName={cell.value} />
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
        Header: (
          <FormContentTitle>
            <FormattedMessage id="admin.tag" />
          </FormContentTitle>
        ),
        accessor: "dockerImageTag",
        collapse: true,
        Cell: ({ cell, row }: CellProps<{ sourceDefinitionId: string }>) => (
          <VersionCell
            version={cell.value}
            id={row.original.sourceDefinitionId}
            onChange={onUpdateVersion}
            feedback={feedbackList[row.original.sourceDefinitionId]}
          />
        ),
      },
    ],
    [feedbackList, onUpdateVersion]
  );

  const usedSources = useMemo<Source[]>(() => {
    const allSources = connections.map((item) => {
      const sourceInfo = sourceDefinitions.find(
        (source) =>
          source.sourceDefinitionId === item.source?.sourceDefinitionId
      );
      return {
        name: item.source?.sourceName,
        sourceDefinitionId: item.source?.sourceDefinitionId || "",
        dockerRepository: sourceInfo?.dockerRepository,
        dockerImageTag: sourceInfo?.dockerImageTag,
        documentationUrl: sourceInfo?.documentationUrl,
        feedback: "",
      };
    });

    const uniqSources = allSources.reduce(
      (map, item) => ({ ...map, [item.sourceDefinitionId]: item }),
      {}
    );

    return Object.values(uniqSources);
  }, [connections, sourceDefinitions]);

  return (
    <>
      {connections.length ? (
        <Block>
          <Title bold>
            <FormattedMessage id="admin.manageSource" />
          </Title>
          <Table columns={columns} data={usedSources} />
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
