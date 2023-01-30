import { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import { HeadTitle } from "components/common/HeadTitle";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Table } from "components/ui/Table";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import ConnectorCell from "./ConnectorCell";
import styles from "./ConnectorsView.module.scss";
import { ConnectorsViewContext } from "./ConnectorsViewContext";
import CreateConnector from "./CreateConnector";
import ImageCell from "./ImageCell";
import UpgradeAllButton from "./UpgradeAllButton";
import VersionCell from "./VersionCell";

interface ConnectorsViewProps {
  type: "sources" | "destinations";
  isUpdateSuccess: boolean;
  hasNewConnectorVersion?: boolean;
  usedConnectorsDefinitions: SourceDefinitionRead[] | DestinationDefinitionRead[];
  connectorsDefinitions: SourceDefinitionRead[] | DestinationDefinitionRead[];
  loading: boolean;
  updatingDefinitionId?: string;
  error?: Error;
  onUpdate: () => void;
  onUpdateVersion: ({ id, version }: { id: string; version: string }) => void;
  feedbackList: Record<string, string>;
}

const defaultSorting = [{ id: "name" }];

const ConnectorsView: React.FC<ConnectorsViewProps> = ({
  type,
  onUpdateVersion,
  feedbackList,
  isUpdateSuccess,
  hasNewConnectorVersion,
  usedConnectorsDefinitions,
  loading,
  updatingDefinitionId,
  error,
  onUpdate,
  connectorsDefinitions,
}) => {
  const allowUpdateConnectors = useFeature(FeatureItem.AllowUpdateConnectors);
  const allowUploadCustomImage = useFeature(FeatureItem.AllowUploadCustomImage);
  const workspace = useCurrentWorkspace();
  const availableConnectorDefinitions = useAvailableConnectorDefinitions<ConnectorDefinition>(
    connectorsDefinitions,
    workspace
  );
  const showVersionUpdateColumn = useCallback(
    (definitions: ConnectorDefinition[]) => {
      if (allowUpdateConnectors) {
        return true;
      }
      if (allowUploadCustomImage && definitions.some((definition) => definition.releaseStage === "custom")) {
        return true;
      }
      return false;
    },
    [allowUpdateConnectors, allowUploadCustomImage]
  );

  const renderColumns = useCallback(
    (showVersionUpdateColumn: boolean) => [
      {
        Header: <FormattedMessage id="admin.connectors" />,
        accessor: "name",
        customWidth: 25,
        Cell: ({ cell, row }: CellProps<ConnectorDefinition>) => (
          <ConnectorCell
            connectorName={cell.value}
            img={row.original.icon}
            hasUpdate={allowUpdateConnectors && Connector.hasNewerVersion(row.original)}
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
      ...(showVersionUpdateColumn
        ? [
            {
              Header: (
                <div className={styles.changeToHeader}>
                  <FormattedMessage id="admin.changeTo" />
                </div>
              ),
              accessor: "latestDockerImageTag",
              collapse: true,
              Cell: ({ cell, row }: CellProps<ConnectorDefinition>) =>
                allowUpdateConnectors || (allowUploadCustomImage && row.original.releaseStage === "custom") ? (
                  <VersionCell
                    version={cell.value || row.original.dockerImageTag}
                    id={Connector.id(row.original)}
                    onChange={onUpdateVersion}
                    currentVersion={row.original.dockerImageTag}
                  />
                ) : null,
            },
          ]
        : []),
    ],
    [allowUpdateConnectors, allowUploadCustomImage, onUpdateVersion]
  );

  const renderHeaderControls = (section: "used" | "available") =>
    ((section === "used" && usedConnectorsDefinitions.length > 0) ||
      (section === "available" && usedConnectorsDefinitions.length === 0)) && (
      <FlexContainer>
        {allowUploadCustomImage && <CreateConnector type={type} />}
        <UpgradeAllButton
          disabled={!((hasNewConnectorVersion || isUpdateSuccess) && allowUpdateConnectors)}
          isLoading={loading}
          hasError={!!error && !loading}
          hasSuccess={isUpdateSuccess}
          onUpdate={onUpdate}
        />
      </FlexContainer>
    );

  const ctx = useMemo(
    () => ({
      updatingAll: loading,
      updatingDefinitionId,
      feedbackList,
    }),
    [feedbackList, loading, updatingDefinitionId]
  );

  const usedDefinitionColumns = useMemo(
    () => renderColumns(showVersionUpdateColumn(usedConnectorsDefinitions)),
    [renderColumns, showVersionUpdateColumn, usedConnectorsDefinitions]
  );
  const availableDefinitionColumns = useMemo(
    () => renderColumns(showVersionUpdateColumn(availableConnectorDefinitions)),
    [renderColumns, showVersionUpdateColumn, availableConnectorDefinitions]
  );

  return (
    <ConnectorsViewContext.Provider value={ctx}>
      <div className={styles.connectorsTable}>
        <HeadTitle
          titles={[{ id: "sidebar.settings" }, { id: type === "sources" ? "admin.sources" : "admin.destinations" }]}
        />
        <FlexContainer direction="column" gap="2xl">
          {usedConnectorsDefinitions.length > 0 && (
            <FlexContainer direction="column">
              <FlexContainer className={styles.title} alignItems="center">
                <FlexItem grow>
                  <Heading as="h2">
                    <FormattedMessage id={type === "sources" ? "admin.manageSource" : "admin.manageDestination"} />
                  </Heading>
                </FlexItem>
                {renderHeaderControls("used")}
              </FlexContainer>
              <Table columns={usedDefinitionColumns} data={usedConnectorsDefinitions} sortBy={defaultSorting} />
            </FlexContainer>
          )}

          <FlexContainer direction="column">
            <FlexContainer className={styles.title} alignItems="center">
              <FlexItem grow>
                <Heading as="h2">
                  <FormattedMessage id={type === "sources" ? "admin.availableSource" : "admin.availableDestinations"} />
                </Heading>
              </FlexItem>
              {renderHeaderControls("available")}
            </FlexContainer>
            <Table columns={availableDefinitionColumns} data={availableConnectorDefinitions} sortBy={defaultSorting} />
          </FlexContainer>
        </FlexContainer>
      </div>
    </ConnectorsViewContext.Provider>
  );
};

export default ConnectorsView;
