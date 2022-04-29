import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormikHelpers } from "formik";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button, Card } from "components";
import LoadingSchema from "components/LoadingSchema";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";

import { ConnectionNamespaceDefinition } from "core/domain/connection";
import {
  useConnectionLoad,
  useResetConnection,
  useUpdateConnection,
  ValuesProps,
} from "hooks/services/useConnectionHook";
import { equal } from "utils/objects";
import ConnectionForm from "views/Connection/ConnectionForm";

interface Props {
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

const ReplicationView: React.FC<Props> = ({ onAfterSaveSchema, connectionId }) => {
  const [isModalOpen, setIsUpdateModalOpen] = useState(false);
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(false);
  const [saved, setSaved] = useState(false);
  const [currentValues, setCurrentValues] = useState<ValuesProps>({
    namespaceDefinition: ConnectionNamespaceDefinition.Source,
    namespaceFormat: "",
    schedule: null,
    prefix: "",
    syncCatalog: { streams: [] },
  });

  const { mutateAsync: updateConnection } = useUpdateConnection();
  const { mutateAsync: resetConnection } = useResetConnection();

  const onReset = () => resetConnection(connectionId);

  const { connection: initialConnection, refreshConnectionCatalog } = useConnectionLoad(connectionId);

  const [{ value: connectionWithRefreshCatalog, loading: isRefreshingCatalog }, refreshCatalog] = useAsyncFn(
    refreshConnectionCatalog,
    [connectionId]
  );

  const connection = activeUpdatingSchemaMode ? connectionWithRefreshCatalog : initialConnection;

  const onSubmit = async (values: ValuesProps, formikHelpers?: FormikHelpers<ValuesProps>) => {
    const initialSyncSchema = connection?.syncCatalog;

    await updateConnection({
      ...values,
      connectionId,
      status: initialConnection.status || "",
      withRefreshedCatalog: activeUpdatingSchemaMode,
      sourceCatalogId: connection?.catalogId,
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

  const onSubmitResetModal = async () => {
    setIsUpdateModalOpen(false);
    await onSubmit(currentValues);
  };

  const onSubmitForm = async (values: ValuesProps) => {
    if (activeUpdatingSchemaMode) {
      setCurrentValues(values);
      setIsUpdateModalOpen(true);
    } else {
      await onSubmit(values);
    }
  };

  const onEnterRefreshCatalogMode = async () => {
    setActiveUpdatingSchemaMode(true);
    await refreshCatalog();
  };

  const onExitRefreshCatalogMode = () => {
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
            isEditMode
            connection={connection}
            onSubmit={onSubmitForm}
            onReset={onReset}
            successMessage={saved && <FormattedMessage id="form.changesSaved" />}
            onCancel={onExitRefreshCatalogMode}
            editSchemeMode={activeUpdatingSchemaMode}
            additionalSchemaControl={renderUpdateSchemaButton()}
          />
        ) : (
          <LoadingSchema />
        )}
      </Card>
      {isModalOpen ? (
        <ResetDataModal
          onClose={() => setIsUpdateModalOpen(false)}
          onSubmit={onSubmitResetModal}
          modalType={ModalTypes.UPDATE_SCHEMA}
        />
      ) : null}
    </Content>
  );
};

export default ReplicationView;
