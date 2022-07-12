import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button, Card } from "components";
import LoadingSchema from "components/LoadingSchema";

import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { ConnectionStateType, ConnectionStatus } from "core/request/AirbyteClient";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import {
  useConnectionLoad,
  useConnectionService,
  useUpdateConnection,
  ValuesProps,
} from "hooks/services/useConnectionHook";
import { equal } from "utils/objects";
import ConnectionForm from "views/Connection/ConnectionForm";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

interface ReplicationViewProps {
  onAfterSaveSchema: () => void;
  connectionId: string;
}

const Content = styled.div`
  max-width: 1279px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

export const ReplicationView: React.FC<ReplicationViewProps> = ({ onAfterSaveSchema, connectionId }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(false);
  const [saved, setSaved] = useState(false);
  const [connectionFormValues, setConnectionFormValues] = useState<FormikConnectionFormValues>();
  const connectionService = useConnectionService();

  console.log("saved", saved);

  const { mutateAsync: updateConnection } = useUpdateConnection();

  const { connection: initialConnection, refreshConnectionCatalog } = useConnectionLoad(connectionId);

  const [{ value: connectionWithRefreshCatalog, loading: isRefreshingCatalog }, refreshCatalog] = useAsyncFn(
    refreshConnectionCatalog,
    [connectionId]
  );

  const connection = useMemo(() => {
    if (activeUpdatingSchemaMode && connectionWithRefreshCatalog) {
      // merge connectionFormValues (unsaved previous form state) with the refreshed connection data:
      // 1. if there is a namespace definition, format, prefix, or schedule in connectionFormValues,
      //    use those and fill in the rest from the database
      // 2. otherwise, use the values from the database
      // 3. if none of the above, use the default values.
      return {
        ...connectionWithRefreshCatalog,
        namespaceDefinition:
          connectionFormValues?.namespaceDefinition ?? connectionWithRefreshCatalog.namespaceDefinition,
        namespaceFormat: connectionFormValues?.namespaceFormat ?? connectionWithRefreshCatalog.namespaceFormat,
        prefix: connectionFormValues?.prefix ?? connectionWithRefreshCatalog.prefix,
        schedule: connectionFormValues?.schedule ?? connectionWithRefreshCatalog.schedule,
      };
    }
    return initialConnection;
  }, [activeUpdatingSchemaMode, connectionWithRefreshCatalog, initialConnection, connectionFormValues]);

  const saveConnection = async (values: ValuesProps, skipReset = false) => {
    const initialSyncSchema = connection.syncCatalog;
    const connectionAsUpdate = toWebBackendConnectionUpdate(connection);

    console.log("skipReset", skipReset);

    await updateConnection({
      ...connectionAsUpdate,
      ...values,
      connectionId,
      // Use the name and status from the initial connection because
      // The status can be toggled and the name can be changed in-between refreshing the schema
      name: initialConnection.name,
      status: initialConnection.status || "",
      // TODO: skipRefresh: true/false
      // skipReset,
    });

    setSaved(true);
    if (!equal(values.syncCatalog, initialSyncSchema)) {
      onAfterSaveSchema();
    }

    if (activeUpdatingSchemaMode) {
      setActiveUpdatingSchemaMode(false);
    }
  };

  const onSubmitForm = async (values: ValuesProps) => {
    console.log("values.syncCatalog", values.syncCatalog);
    console.log("initialConnection", initialConnection.syncCatalog);
    const hasCatalogChanged = !equal(values.syncCatalog, initialConnection.syncCatalog);

    console.log("hasCatalogChanged?", hasCatalogChanged);
    if (hasCatalogChanged) {
      const stateType = await connectionService.getStateType(connectionId);
      console.log("ConnectionStateType", stateType);
      if (stateType === ConnectionStateType.legacy) {
        // The state type is legacy so the server will do a full reset after saving
        // TODO: Show confirm dialog with full reset option
        openConfirmationModal({
          title: "connection.updateSchema",
          text: "connection.updateSchemaText",
          submitButtonText: "connection.updateSchema",
          submitButtonDataId: "refresh",
          secondaryButtonText: "connection.updateSchemaWithoutReset",
          onSubmit: async (type) => {
            await saveConnection(values, type === "secondary");
            closeConfirmationModal();
          },
        });
      } else {
        // TODO: Show confirm dialog with partial reset option
        openConfirmationModal({
          title: "connection.updateSchema",
          text: "connection.updateSchemaText",
          submitButtonText: "connection.updateSchema",
          submitButtonDataId: "refresh",
          secondaryButtonText: "connection.updateSchemaWithoutReset",
          onSubmit: async (type) => {
            await saveConnection(values, type === "secondary");
            closeConfirmationModal();
          },
        });
      }
      // const skipRefresh = true;
      // await saveConnection(values, skipRefresh);
    } else {
      // The catalog hasn't changed. We don't need to ask for any confirmation and can simply save
      // TODO: Clarify if we want to have `skipRefresh` true or false in this case with BE.
      await saveConnection(values, true);
    }
  };

  const onRefreshSourceSchema = async () => {
    setSaved(false);
    setActiveUpdatingSchemaMode(true);
    await refreshCatalog();
  };

  const onCancelConnectionFormEdit = () => {
    setSaved(false);
    setActiveUpdatingSchemaMode(false);
  };

  return (
    <Content>
      <Card>
        {!isRefreshingCatalog && connection ? (
          <ConnectionForm
            mode={connection?.status !== ConnectionStatus.deprecated ? "edit" : "readonly"}
            connection={connection}
            onSubmit={onSubmitForm}
            successMessage={saved && <FormattedMessage id="form.changesSaved" />}
            onCancel={onCancelConnectionFormEdit}
            allowSavingUntouchedForm={activeUpdatingSchemaMode}
            additionalSchemaControl={
              <Button onClick={onRefreshSourceSchema} type="button" secondary>
                <TryArrow icon={faSyncAlt} />
                <FormattedMessage id="connection.updateSchema" />
              </Button>
            }
            onChangeValues={setConnectionFormValues}
          />
        ) : (
          <LoadingSchema />
        )}
      </Card>
    </Content>
  );
};
