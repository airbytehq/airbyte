import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import Table from "components/Table";
import ConnectorCell from "./ConnectorCell";
import ImageCell from "./ImageCell";
import VersionCell from "./VersionCell";
import { Block, FormContentTitle, Title } from "./PageComponents";
import { SourceDefinition } from "core/resources/SourceDefinition";
import UpgradeAllButton from "./UpgradeAllButton";
import CreateConnector from "./CreateConnector";
import HeadTitle from "components/HeadTitle";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

type ConnectorsViewProps = {
  type: "sources" | "destinations";
  isUpdateSuccess: boolean;
  hasNewConnectorVersion?: boolean;
  onUpdateVersion: ({ id, version }: { id: string; version: string }) => void;
  usedConnectorsDefinitions: SourceDefinition[] | DestinationDefinition[];
  connectorsDefinitions: SourceDefinition[] | DestinationDefinition[];
  loading: boolean;
  error?: Error;
  onUpdate: () => void;
  feedbackList: Record<string, string>;
};

const ConnectorsView: React.FC<ConnectorsViewProps> = ({
  type,
  onUpdateVersion,
  feedbackList,
  isUpdateSuccess,
  hasNewConnectorVersion,
  usedConnectorsDefinitions,
  loading,
  error,
  onUpdate,
  connectorsDefinitions,
}) => {
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
          icon?: string;
        }>) => (
          <ConnectorCell
            connectorName={cell.value}
            img={row.original.icon}
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

  return (
    <>
      <HeadTitle
        titles={[
          { id: "sidebar.settings" },
          { id: type === "sources" ? "admin.sources" : "admin.destinations" },
        ]}
      />
      {usedConnectorsDefinitions.length ? (
        <Block>
          <Title bold>
            <FormattedMessage
              id={
                type === "sources"
                  ? "admin.manageSource"
                  : "admin.manageDestination"
              }
            />
            <div>
              <CreateConnector type={type} />
              {(hasNewConnectorVersion || isUpdateSuccess) && (
                <UpgradeAllButton
                  isLoading={loading}
                  hasError={!!error && !loading}
                  hasSuccess={isUpdateSuccess}
                  onUpdate={onUpdate}
                />
              )}
            </div>
          </Title>
          <Table columns={columns} data={usedConnectorsDefinitions} />
        </Block>
      ) : null}

      <Block>
        <Title bold>
          <FormattedMessage
            id={
              type === "sources"
                ? "admin.availableSource"
                : "admin.availableDestinations"
            }
          />
          {(hasNewConnectorVersion || isUpdateSuccess) &&
            !usedConnectorsDefinitions.length && (
              <UpgradeAllButton
                isLoading={loading}
                hasError={!!error && !loading}
                hasSuccess={isUpdateSuccess}
                onUpdate={onUpdate}
              />
            )}
        </Title>
        <Table columns={columns} data={connectorsDefinitions} />
      </Block>
    </>
  );
};

export default ConnectorsView;
