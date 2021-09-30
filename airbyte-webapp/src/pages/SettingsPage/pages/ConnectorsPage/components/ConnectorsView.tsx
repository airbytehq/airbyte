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
import { Connector, ConnectorDefinition } from "core/domain/connector";
import { WithFeature } from "hooks/services/Feature";

type ConnectorsViewProps = {
  type: "sources" | "destinations";
  isUpdateSuccess: boolean;
  hasNewConnectorVersion?: boolean;
  usedConnectorsDefinitions: SourceDefinition[] | DestinationDefinition[];
  connectorsDefinitions: SourceDefinition[] | DestinationDefinition[];
  loading: boolean;
  error?: Error;
  onUpdate: () => void;
  onUpdateVersion: ({ id, version }: { id: string; version: string }) => void;
  feedbackList: Record<string, string>;
};

const defaultSorting = [{ id: "name" }];

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
        Cell: ({ cell, row }: CellProps<ConnectorDefinition>) => (
          <ConnectorCell
            connectorName={cell.value}
            img={row.original.icon}
            hasUpdate={Connector.hasNewerVersion(row.original)}
          />
        ),
      },
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "dockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<ConnectorDefinition>) => (
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
        Cell: ({ cell, row }: CellProps<ConnectorDefinition>) => (
          <VersionCell
            version={cell.value}
            id={Connector.id(row.original)}
            onChange={onUpdateVersion}
            feedback={feedbackList[Connector.id(row.original)]}
            currentVersion={row.original.dockerImageTag}
          />
        ),
      },
    ],
    [feedbackList, onUpdateVersion]
  );

  const renderHeaderControls = (section: "used" | "available") =>
    ((section === "used" && usedConnectorsDefinitions.length > 0) ||
      (section === "available" && usedConnectorsDefinitions.length === 0)) && (
      <div>
        <WithFeature featureId={"ALLOW_UPLOAD_CUSTOM_IMAGE"}>
          <CreateConnector type={type} />
        </WithFeature>
        {(hasNewConnectorVersion || isUpdateSuccess) && (
          <UpgradeAllButton
            isLoading={loading}
            hasError={!!error && !loading}
            hasSuccess={isUpdateSuccess}
            onUpdate={onUpdate}
          />
        )}
      </div>
    );

  return (
    <>
      <HeadTitle
        titles={[
          { id: "sidebar.settings" },
          { id: type === "sources" ? "admin.sources" : "admin.destinations" },
        ]}
      />
      {usedConnectorsDefinitions.length > 0 && (
        <Block>
          <Title bold>
            <FormattedMessage
              id={
                type === "sources"
                  ? "admin.manageSource"
                  : "admin.manageDestination"
              }
            />
            {renderHeaderControls("used")}
          </Title>
          <Table
            columns={columns}
            data={usedConnectorsDefinitions}
            sortBy={defaultSorting}
          />
        </Block>
      )}

      <Block>
        <Title bold>
          <FormattedMessage
            id={
              type === "sources"
                ? "admin.availableSource"
                : "admin.availableDestinations"
            }
          />
          {renderHeaderControls("available")}
        </Title>
        <Table
          columns={columns}
          data={connectorsDefinitions}
          sortBy={defaultSorting}
        />
      </Block>
    </>
  );
};

export default ConnectorsView;
