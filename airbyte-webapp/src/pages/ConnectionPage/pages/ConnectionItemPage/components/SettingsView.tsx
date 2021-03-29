import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";

import ContentCard from "components/ContentCard";
import FrequencyConfig from "data/FrequencyConfig.json";
import useConnection, {
  useConnectionLoad,
} from "components/hooks/services/useConnectionHook";
import DeleteBlock from "components/DeleteBlock";
import FrequencyForm from "views/Connector/FrequencyForm";
import { SyncSchema } from "core/domain/catalog";
import { equal } from "utils/objects";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";
import Button from "components/Button";
import LoadingSchema from "components/LoadingSchema";
import EnabledControl from "./EnabledControl";

type IProps = {
  onAfterSaveSchema: () => void;
  connectionId: string;
  frequencyText?: string;
};

const Content = styled.div`
  max-width: 1140px;
  overflow-x: hidden;
  margin: 18px auto;
`;

const TitleContainer = styled.div<{ hasButton: boolean }>`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin: ${({ hasButton }) => (hasButton ? "-5px 0" : 0)};
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

const Title = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Message = styled.div`
  margin: -5px 0 13px;
  font-weight: 500;
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
`;

const Note = styled.span`
  color: ${({ theme }) => theme.dangerColor};
`;

type FormValues = {
  frequency: string;
  prefix: string;
  schema: SyncSchema;
};

const SettingsView: React.FC<IProps> = ({
  onAfterSaveSchema,
  connectionId,
  frequencyText,
}) => {
  const [isModalOpen, setIsUpdateModalOpen] = useState(false);
  const [activeUpdatingSchemaMode, setActiveUpdatingSchemaMode] = useState(
    false
  );
  const formatMessage = useIntl().formatMessage;
  const [saved, setSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentValues, setCurrentValues] = useState<FormValues>({
    frequency: "",
    prefix: "",
    schema: { streams: [] },
  });
  const [errorMessage, setErrorMessage] = useState("");
  const {
    updateConnection,
    deleteConnection,
    resetConnection,
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
    connectionId,
  ]);

  const schedule =
    connection &&
    FrequencyConfig.find((item) => equal(connection.schedule, item.config));

  const onSubmit = async (values: FormValues) => {
    setIsLoading(true);
    const frequencyData = FrequencyConfig.find(
      (item) => item.value === values.frequency
    );
    const initialSyncSchema = connection?.syncCatalog;

    try {
      await updateConnection({
        connectionId: connectionId,
        syncCatalog: values.schema,
        status: connection?.status || "",
        schedule: frequencyData?.config || null,
        prefix: values.prefix,
        withRefreshedCatalog: activeUpdatingSchemaMode,
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
            id: "form.someError",
          })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmitResetModal = async () => {
    setIsUpdateModalOpen(false);
    await onSubmit(currentValues);
  };

  const onSubmitForm = async (values: FormValues) => {
    if (activeUpdatingSchemaMode) {
      setCurrentValues(values);
      setIsUpdateModalOpen(true);
    } else {
      await onSubmit(values);
    }
  };

  const UpdateSchemaButton = () => {
    if (!activeUpdatingSchemaMode) {
      return (
        <Button onClick={() => setActiveUpdatingSchemaMode(true)} type="button">
          <TryArrow icon={faRedoAlt} />
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
      <ContentCard
        title={
          <Title>
            <TitleContainer hasButton={!activeUpdatingSchemaMode}>
              <FormattedMessage id="connection.connectionSettings" />{" "}
            </TitleContainer>
            {!connection ? null : (
              <EnabledControl
                connection={connection}
                frequencyText={frequencyText}
              />
            )}
          </Title>
        }
      >
        {!isLoadingConnection && connection ? (
          <FrequencyForm
            isEditMode
            schema={connection.syncCatalog}
            onSubmit={onSubmitForm}
            onReset={onReset}
            frequencyValue={schedule?.value}
            prefixValue={connection.prefix}
            errorMessage={errorMessage}
            successMessage={
              saved && <FormattedMessage id="form.changesSaved" />
            }
            onCancel={() => setActiveUpdatingSchemaMode(false)}
            editSchemeMode={activeUpdatingSchemaMode}
            isLoading={isLoading}
            additionalSchemaControl={UpdateSchemaButton()}
            source={connection.source}
            destination={connection.destination}
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
