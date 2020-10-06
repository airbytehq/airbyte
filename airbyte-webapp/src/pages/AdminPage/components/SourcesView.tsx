import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";
import { useResource } from "rest-hooks";

import Table from "../../../components/Table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import ConnectionResource from "../../../core/resources/Connection";
import config from "../../../config";
import { Block, Title } from "./PageComponents";
import SourceResource from "../../../core/resources/Source";

const SourcesView: React.FC = () => {
  const { connections } = useResource(ConnectionResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });

  const columns = React.useMemo(
    () => [
      {
        Header: <FormattedMessage id="admin.connectors" />,
        accessor: "name",
        customWidth: 34,
        Cell: ({ cell }: CellProps<{}>) => (
          <ConnectorCell connectorName={cell.value} />
        )
      },
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "defaultDockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<{ imageLink: string }>) => (
          <ImageCell imageName={cell.value} link={row.original.imageLink} />
        )
      }
    ],
    []
  );
  const columnsCurrentSources = React.useMemo(
    () => [
      ...columns,
      {
        Header: <FormattedMessage id="admin.version" />,
        accessor: "defaultDockerImageVersion",
        collapse: true,
        Cell: ({ cell }: CellProps<{}>) => <VersionCell version={cell.value} />
      }
    ],
    [columns]
  );

  const columnsAllSources = React.useMemo(
    () => [
      ...columns,
      {
        Header: "",
        accessor: "version",
        collapse: true,
        Cell: () => <VersionCell empty />
      }
    ],
    [columns]
  );

  const usedSources = connections.map(item => {
    const sourceInfo = sources.find(
      source => source.sourceId === item.source?.sourceId
    );
    return {
      name: item.source?.sourceName,
      defaultDockerRepository: sourceInfo?.defaultDockerRepository,
      defaultDockerImageVersion: sourceInfo?.defaultDockerImageVersion
    };
  });

  return (
    <>
      {connections.length ? (
        <Block>
          <Title bold>
            <FormattedMessage id="admin.manageSource" />
          </Title>
          <Table columns={columnsCurrentSources} data={usedSources} />
        </Block>
      ) : null}

      <Block>
        <Title bold>
          <FormattedMessage id="admin.availableSource" />
        </Title>
        <Table columns={columnsAllSources} data={sources} />
      </Block>
    </>
  );
};

export default SourcesView;
