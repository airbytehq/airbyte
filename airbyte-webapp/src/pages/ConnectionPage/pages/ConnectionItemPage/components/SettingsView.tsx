import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import { Connection } from "../../../../../core/resources/Connection";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import useConnection from "../../../../../components/hooks/services/useConnectionHook";
import DeleteBlock from "../../../../../components/DeleteBlock";
import FrequencyForm from "../../../../../components/FrequencyForm";
import { SyncSchema } from "../../../../../core/resources/Schema";
import { equal } from "../../../../../utils/objects";
import ResetDataModal from "../../../../../components/ResetDataModal";
import { ModalTypes } from "../../../../../components/ResetDataModal/types";

type IProps = {
  connection: Connection;
  isModalOpen?: boolean;
  activeUpdatingSchemaMode?: boolean;
  deactivatedUpdatingSchemaMode: () => void;
  onAfterSaveSchema: () => void;
  setModalState: (state: boolean) => void;
  onSubmitModal: () => void;
};

const Content = styled.div`
  max-width: 813px;
  margin: 18px auto;
`;

const SettingsView: React.FC<IProps> = ({
  connection,
  onAfterSaveSchema,
  isModalOpen,
  setModalState,
  onSubmitModal,
  activeUpdatingSchemaMode,
  deactivatedUpdatingSchemaMode
}) => {
  const formatMessage = useIntl().formatMessage;
  const [saved, setSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentValues, setCurrentValues] = useState<{
    frequency: string;
    schema: SyncSchema;
  }>({ frequency: "", schema: { streams: [] } });
  const [errorMessage, setErrorMessage] = useState("");
  const {
    updateConnection,
    deleteConnection,
    resetConnection
  } = useConnection();

  const schedule = FrequencyConfig.find(item =>
    equal(connection.schedule, item.config)
  );

  const onSubmitResetModal = async () => {
    if (activeUpdatingSchemaMode) {
      setModalState(false);
      await onSubmit(currentValues);
    } else {
      onSubmitModal();
    }
  };

  const onSubmitForm = async (values: {
    frequency: string;
    schema: SyncSchema;
  }) => {
    if (activeUpdatingSchemaMode) {
      setCurrentValues(values);
      setModalState(true);
    } else {
      await onSubmit(values);
    }
  };

  const onSubmit = async (values: {
    frequency: string;
    schema: SyncSchema;
  }) => {
    setIsLoading(true);
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    const initialSyncSchema = connection.syncSchema;

    try {
      await updateConnection({
        connectionId: connection.connectionId,
        syncSchema: values.schema,
        status: connection.status,
        schedule: frequencyData?.config || null,
        with_refreshed_catalog: activeUpdatingSchemaMode
      });

      setSaved(true);
      if (!equal(values.schema, initialSyncSchema)) {
        onAfterSaveSchema();
      }

      if (activeUpdatingSchemaMode) {
        deactivatedUpdatingSchemaMode();
      }
    } catch (e) {
      setErrorMessage(
        e.message ||
          formatMessage({
            id: "form.someError"
          })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const onDelete = useCallback(
    () => deleteConnection({ connectionId: connection.connectionId }),
    [deleteConnection, connection.connectionId]
  );

  const onReset = useCallback(() => resetConnection(connection.connectionId), [
    resetConnection,
    connection.connectionId
  ]);

  return (
    <Content>
      <ContentCard
        title={<FormattedMessage id="connection.connectionSettings" />}
      >
        <FrequencyForm
          isEditMode
          schema={connection.syncSchema}
          onSubmit={onSubmitForm}
          onReset={onReset}
          frequencyValue={schedule?.value}
          errorMessage={errorMessage}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
          onCancel={deactivatedUpdatingSchemaMode}
          editSchemeMode={activeUpdatingSchemaMode}
          isLoading={isLoading}
        />
      </ContentCard>
      <DeleteBlock type="connection" onDelete={onDelete} />
      {isModalOpen ? (
        <ResetDataModal
          onClose={() => setModalState(false)}
          onSubmit={onSubmitResetModal}
          modalType={ModalTypes.UPDATE_SCHEMA}
        />
      ) : null}
    </Content>
  );
};

export default SettingsView;
