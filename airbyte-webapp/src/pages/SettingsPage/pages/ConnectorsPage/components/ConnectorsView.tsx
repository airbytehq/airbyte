import React from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import HeadTitle from "components/HeadTitle";
import Table from "components/Table";

import { Connector, ConnectorDefinition, DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { FeatureItem, useFeatureService, WithFeature } from "hooks/services/Feature";

import ConnectorCell from "./ConnectorCell";
import CreateConnector from "./CreateConnector";
import ImageCell from "./ImageCell";
import { Block, FormContentTitle, Title } from "./PageComponents";
import UpgradeAllButton from "./UpgradeAllButton";
import VersionCell from "./VersionCell";

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
  const { hasFeature } = useFeatureService();
  const allowUpdateConnectors = hasFeature(FeatureItem.AllowUpdateConnectors);

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
            hasUpdate={allowUpdateConnectors && Connector.hasNewerVersion(row.original)}
            isDeprecated={Connector.isDeprecated(row.original)}
            releaseStage={row.original.releaseStage}
          />
        ),
      },
      {
        Header: <FormattedMessage id="admin.image" />,
        accessor: "dockerRepository",
        customWidth: 36,
        Cell: ({ cell, row }: CellProps<ConnectorDefinition>) => (
          <ImageCell imageName={cell.value} link={row.original.documentationUrl} />
        ),
      },
      {
        Header: <FormattedMessage id="admin.currentVersion" />,
        accessor: "dockerImageTag",
        customWidth: 10,
      },
      ...(allowUpdateConnectors
        ? [
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
                  version={cell.value || row.original.dockerImageTag}
                  id={Connector.id(row.original)}
                  onChange={onUpdateVersion}
                  feedback={feedbackList[Connector.id(row.original)]}
                  currentVersion={row.original.dockerImageTag}
                />
              ),
            },
          ]
        : []),
    ],
    [feedbackList, onUpdateVersion, allowUpdateConnectors]
  );

  const renderHeaderControls = (section: "used" | "available") =>
    ((section === "used" && usedConnectorsDefinitions.length > 0) ||
      (section === "available" && usedConnectorsDefinitions.length === 0)) && (
      <div>
        <WithFeature featureId={FeatureItem.AllowUploadCustomImage}>
          <CreateConnector type={type} />
        </WithFeature>
        {(hasNewConnectorVersion || isUpdateSuccess) && allowUpdateConnectors && (
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
        titles={[{ id: "sidebar.settings" }, { id: type === "sources" ? "admin.sources" : "admin.destinations" }]}
      />
      {usedConnectorsDefinitions.length > 0 && (
        <Block>
          <Title bold>
            <FormattedMessage id={type === "sources" ? "admin.manageSource" : "admin.manageDestination"} />
            {renderHeaderControls("used")}
          </Title>
          <Table columns={columns} data={usedConnectorsDefinitions} sortBy={defaultSorting} />
        </Block>
      )}

      <Block>
        <Title bold>
          <FormattedMessage id={type === "sources" ? "admin.availableSource" : "admin.availableDestinations"} />
          {renderHeaderControls("available")}
        </Title>
        <Table columns={columns} data={connectorsDefinitions} sortBy={defaultSorting} />
      </Block>
    </>
  );
};

export default ConnectorsView;
