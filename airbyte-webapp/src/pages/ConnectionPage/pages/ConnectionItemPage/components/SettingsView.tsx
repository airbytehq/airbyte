import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import useConnection, {
  useConnectionLoad
} from "../../../../../components/hooks/services/useConnectionHook";
import DeleteBlock from "../../../../../components/DeleteBlock";
import FrequencyForm from "../../../../../components/FrequencyForm";
import { SyncSchema } from "../../../../../core/domain/catalog";
import { equal } from "../../../../../utils/objects";
import ResetDataModal from "../../../../../components/ResetDataModal";
import { ModalTypes } from "../../../../../components/ResetDataModal/types";
import Button from "../../../../../components/Button";
import LoadingSchema from "../../../../../components/LoadingSchema";

type IProps = {
  onAfterSaveSchema: () => void;
  connectionId: string;
};

const Content = styled.div`
  max-width: 813px;
  margin: 18px auto;
`;

const TitleContainer = styled.div<{ hasButton: boolean }>`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin: ${({ hasButton }) => (hasButton ? "-5px 0" : 0)};
`;

const SettingsView: React.FC<IProps> = ({
  onAfterSaveSchema,
  connectionId
}) => {
  const [isModalOpen, setIsUpdateModalOpen] = useState(false);
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(
    false
  );
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

  const { connection, isLoadingConnection } = useConnectionLoad(
    connectionId,
    activeUpdatingSchemaMode
  );

  const onDelete = useCallback(
    () => deleteConnection({ connectionId: connectionId }),
    [deleteConnection, connectionId]
  );

  const onReset = useCallback(() => resetConnection(connectionId), [
    resetConnection,
    connectionId
  ]);

  const schedule =
    connection &&
    FrequencyConfig.find(item => equal(connection.schedule, item.config));

  const onSubmitResetModal = async () => {
    if (activeUpdatingSchemaMode) {
      setIsUpdateModalOpen(false);
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
      setIsUpdateModalOpen(true);
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
    const initialSyncSchema = connection?.syncCatalog;

    try {
      await updateConnection({
        connectionId: connectionId,
        syncCatalog: values.schema,
        status: connection?.status || "",
        schedule: frequencyData?.config || null,
        withRefreshedCatalog: activeUpdatingSchemaMode
      });

      setSaved(true);
      if (!equal(values.schema, initialSyncSchema)) {
        onAfterSaveSchema();
      }

      if (activeUpdatingSchemaMode) {
        setActiveUpdatingSchemaMode(false);
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

  const onSubmitModal = () => {
    setActiveUpdatingSchemaMode(true);
    setIsUpdateModalOpen(false);
  };

  const endControl = () => {
    if (!activeUpdatingSchemaMode) {
      return (
        <Button onClick={() => setIsUpdateModalOpen(true)}>
          <FormattedMessage id="connection.updateSchema" />
        </Button>
      );
    }
    return null;
  };

  return (
    <Content>
      <ContentCard
        title={
          <TitleContainer hasButton={!activeUpdatingSchemaMode}>
            <FormattedMessage id="connection.connectionSettings" />{" "}
            {endControl()}
          </TitleContainer>
        }
      >
        {!isLoadingConnection && connection ? (
          <FrequencyForm
            isEditMode
            schema={connection.syncCatalog}
            onSubmit={onSubmitForm}
            onReset={onReset}
            frequencyValue={schedule?.value}
            errorMessage={errorMessage}
            successMessage={
              saved && <FormattedMessage id="form.changesSaved" />
            }
            onCancel={() => setActiveUpdatingSchemaMode(false)}
            editSchemeMode={activeUpdatingSchemaMode}
            isLoading={isLoading}
          />
        ) : (
          <LoadingSchema />
        )}
      </ContentCard>
      <DeleteBlock type="connection" onDelete={onDelete} />
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

export default SettingsView;
