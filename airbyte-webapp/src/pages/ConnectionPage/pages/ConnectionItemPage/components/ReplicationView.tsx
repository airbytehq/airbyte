import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormikHelpers } from "formik";
import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button, Card } from "components";
import LoadingSchema from "components/LoadingSchema";

import { toWebBackendConnectionUpdate } from "core/domain/connection";
import { ConnectionStatus } from "core/request/AirbyteClient";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import {
  useConnectionLoad,
  useResetConnection,
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

const Message = styled.div`
  font-weight: 500;
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
`;

const Note = styled.span`
  color: ${({ theme }) => theme.dangerColor};
`;

export const ReplicationView: React.FC<ReplicationViewProps> = ({ onAfterSaveSchema, connectionId }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(false);
  const [saved, setSaved] = useState(false);
  const [connectionFormValues, setConnectionFormValues] = useState<FormikConnectionFormValues>();

  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: resetConnection } = useResetConnection();

  const onReset = () => resetConnection(connectionId);

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

  const onSubmit = async (values: ValuesProps, formikHelpers?: FormikHelpers<ValuesProps>) => {
    if (!connection) {
      // onSubmit should only be called when a connection object exists.
      return;
    }

    const initialSyncSchema = connection.syncCatalog;
    const connectionAsUpdate = toWebBackendConnectionUpdate(connection);

    await updateConnection({
      ...connectionAsUpdate,
      ...values,
      connectionId,
      // Use the name and status from the initial connection because
      // The status can be toggled and the name can be changed in-between refreshing the schema
      name: initialConnection.name,
      status: initialConnection.status || "",
      withRefreshedCatalog: activeUpdatingSchemaMode,
    });

    setSaved(true);
    if (!equal(values.syncCatalog, initialSyncSchema)) {
      onAfterSaveSchema();
    }

    if (activeUpdatingSchemaMode) {
      setActiveUpdatingSchemaMode(false);
    }

    formikHelpers?.resetForm({ values });
  };

  const openResetDataModal = (values: ValuesProps) => {
    openConfirmationModal({
      title: "connection.updateSchema",
      text: "connection.updateSchemaText",
      submitButtonText: "connection.updateSchema",
      submitButtonDataId: "refresh",
      onSubmit: async () => {
        await onSubmit(values);
        closeConfirmationModal();
      },
    });
  };

  const onSubmitForm = async (values: ValuesProps) => {
    if (activeUpdatingSchemaMode) {
      openResetDataModal(values);
    } else {
      await onSubmit(values);
    }
  };

  const onEnterRefreshCatalogMode = async () => {
    setActiveUpdatingSchemaMode(true);
    await refreshCatalog();
  };

  const onCancelConnectionFormEdit = () => {
    setActiveUpdatingSchemaMode(false);
  };

  const renderUpdateSchemaButton = () => {
    if (!activeUpdatingSchemaMode) {
      return (
        <Button onClick={onEnterRefreshCatalogMode} type="button" secondary>
          <TryArrow icon={faSyncAlt} />
          <FormattedMessage id="connection.updateSchema" />
        </Button>
      );
    }
    return (
      <Message>
        <FormattedMessage id="form.toSaveSchema" />{" "}
        <Note>
          <FormattedMessage id="form.noteStartSync" />
        </Note>
      </Message>
    );
  };

  return (
    <Content>
      <Card>
        {!isRefreshingCatalog && connection ? (
          <ConnectionForm
            mode={connection?.status !== ConnectionStatus.deprecated ? "edit" : "readonly"}
            connection={connection}
            onSubmit={onSubmitForm}
            onReset={onReset}
            successMessage={saved && <FormattedMessage id="form.changesSaved" />}
            onCancel={onCancelConnectionFormEdit}
            editSchemeMode={activeUpdatingSchemaMode}
            additionalSchemaControl={renderUpdateSchemaButton()}
            onChangeValues={setConnectionFormValues}
          />
        ) : (
          <LoadingSchema />
        )}
      </Card>
    </Content>
  );
};
