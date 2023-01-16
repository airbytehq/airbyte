import { CellContext, ColumnDef, ColumnSort } from "@tanstack/react-table";
import { useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { NextTable } from "components/ui/NextTable";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import ConnectorCell from "./ConnectorCell";
import styles from "./ConnectorsView.module.scss";
import CreateConnector from "./CreateConnector";
import ImageCell from "./ImageCell";
import { Block, FormContentTitle, Title } from "./PageComponents";
import UpgradeAllButton from "./UpgradeAllButton";
import VersionCell from "./VersionCell";

interface ConnectorsViewProps {
  type: "sources" | "destinations";
  isUpdateSuccess: boolean;
  hasNewConnectorVersion?: boolean;
  usedConnectorsDefinitions: SourceDefinitionRead[] | DestinationDefinitionRead[];
  connectorsDefinitions: SourceDefinitionRead[] | DestinationDefinitionRead[];
  loading: boolean;
  error?: Error;
  onUpdate: () => void;
  onUpdateVersion: ({ id, version }: { id: string; version: string }) => void;
  feedbackList: Record<string, string>;
}

const defaultSorting: ColumnSort[] = [{ id: "name", desc: false }];

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
    (
      showVersionUpdateColumn: boolean
    ): Array<ColumnDef<ConnectorDefinition, string> | ColumnDef<ConnectorDefinition>> => [
      {
        header: () => <FormattedMessage id="admin.connectors" />,
        accessorKey: "name",
        meta: {
          thClassName: styles.thName,
        },
        cell: (props: CellContext<ConnectorDefinition, string>) => (
          <ConnectorCell
            connectorName={props.cell.getValue()}
            img={props.row.original.icon}
            hasUpdate={allowUpdateConnectors && Connector.hasNewerVersion(props.row.original)}
            releaseStage={props.row.original.releaseStage}
          />
        ),
      },
      {
        header: () => <FormattedMessage id="admin.image" />,
        accessorKey: "dockerRepository",
        meta: {
          thClassName: styles.thDockerRepository,
        },
        cell: (props: CellContext<ConnectorDefinition, string>) => (
          <ImageCell imageName={props.cell.getValue()} link={props.row.original.documentationUrl} />
        ),
      },
      {
        header: () => <FormattedMessage id="admin.currentVersion" />,
        accessorKey: "dockerImageTag",
        meta: {
          thClassName: styles.thDockerImageTag,
        },
      },
      ...(showVersionUpdateColumn
        ? [
            {
              header: () => (
                <FormContentTitle>
                  <FormattedMessage id="admin.changeTo" />
                </FormContentTitle>
              ),
              accessorKey: "latestDockerImageTag",
              meta: {
                collapse: true,
              },
              cell: (props: CellContext<ConnectorDefinition, string>) =>
                allowUpdateConnectors || (allowUploadCustomImage && props.row.original.releaseStage === "custom") ? (
                  <VersionCell
                    version={props.cell.getValue() || props.row.original.dockerImageTag}
                    id={Connector.id(props.row.original)}
                    onChange={onUpdateVersion}
                    feedback={feedbackList[Connector.id(props.row.original)]}
                    currentVersion={props.row.original.dockerImageTag}
                    updating={loading}
                  />
                ) : null,
            },
          ]
        : []),
    ],
    [allowUpdateConnectors, allowUploadCustomImage, onUpdateVersion, feedbackList, loading]
  );

  const renderHeaderControls = (section: "used" | "available") =>
    ((section === "used" && usedConnectorsDefinitions.length > 0) ||
      (section === "available" && usedConnectorsDefinitions.length === 0)) && (
      <div className={styles.buttonsContainer}>
        {allowUploadCustomImage && <CreateConnector type={type} />}
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
          <NextTable
            columns={renderColumns(showVersionUpdateColumn(usedConnectorsDefinitions))}
            data={usedConnectorsDefinitions}
            columnSort={defaultSorting}
          />
        </Block>
      )}

      <Block>
        <Title bold>
          <FormattedMessage id={type === "sources" ? "admin.availableSource" : "admin.availableDestinations"} />
          {renderHeaderControls("available")}
        </Title>
        <NextTable
          columns={renderColumns(showVersionUpdateColumn(availableConnectorDefinitions))}
          data={availableConnectorDefinitions}
          columnSort={defaultSorting}
        />
      </Block>
    </>
  );
};

export default ConnectorsView;
