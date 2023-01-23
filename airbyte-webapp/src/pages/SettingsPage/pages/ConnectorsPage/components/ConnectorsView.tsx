import { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { CellProps } from "react-table";

import { HeadTitle } from "components/common/HeadTitle";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Table } from "components/ui/Table";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { DestinationDefinitionRead, SourceDefinitionRead } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";

import ConnectorCell from "./ConnectorCell";
import CreateConnector from "./CreateConnector";
import ImageCell from "./ImageCell";
import { FormContentTitle } from "./PageComponents";
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
                <FormContentTitle>
                  <FormattedMessage id="admin.changeTo" />
                </FormContentTitle>
              ),
              accessor: "latestDockerImageTag",
              collapse: true,
              Cell: ({ cell, row }: CellProps<ConnectorDefinition>) =>
                allowUpdateConnectors || (allowUploadCustomImage && row.original.releaseStage === "custom") ? (
                  <VersionCell
                    version={cell.value || row.original.dockerImageTag}
                    id={Connector.id(row.original)}
                    onChange={onUpdateVersion}
                    feedback={feedbackList[Connector.id(row.original)]}
                    currentVersion={row.original.dockerImageTag}
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
      <FlexContainer>
        {allowUploadCustomImage && <CreateConnector type={type} />}
        {(hasNewConnectorVersion || isUpdateSuccess) && allowUpdateConnectors && (
          <UpgradeAllButton
            isLoading={loading}
            hasError={!!error && !loading}
            hasSuccess={isUpdateSuccess}
            onUpdate={onUpdate}
          />
        )}
      </FlexContainer>
    );

  return (
    <>
      <HeadTitle
        titles={[{ id: "sidebar.settings" }, { id: type === "sources" ? "admin.sources" : "admin.destinations" }]}
      />
      <FlexContainer direction="column" gap="2xl">
        {usedConnectorsDefinitions.length > 0 && (
          <FlexContainer direction="column" gap="xl">
            <FlexContainer alignItems="center" justifyContent="space-between">
              <Heading as="h2" size="sm">
                <FormattedMessage id={type === "sources" ? "admin.manageSource" : "admin.manageDestination"} />
              </Heading>
              {renderHeaderControls("used")}
            </FlexContainer>
            <Table
              columns={renderColumns(showVersionUpdateColumn(usedConnectorsDefinitions))}
              data={usedConnectorsDefinitions}
              sortBy={defaultSorting}
            />
          </FlexContainer>
        )}

        <FlexContainer direction="column" gap="xl">
          <FlexContainer alignItems="center" justifyContent="space-between">
            <Heading as="h2" size="sm">
              <FormattedMessage id={type === "sources" ? "admin.availableSource" : "admin.availableDestinations"} />
            </Heading>
            {renderHeaderControls("available")}
          </FlexContainer>
          <Table
            columns={renderColumns(showVersionUpdateColumn(availableConnectorDefinitions))}
            data={availableConnectorDefinitions}
            sortBy={defaultSorting}
          />
        </FlexContainer>
      </FlexContainer>
    </>
  );
};

export default ConnectorsView;
