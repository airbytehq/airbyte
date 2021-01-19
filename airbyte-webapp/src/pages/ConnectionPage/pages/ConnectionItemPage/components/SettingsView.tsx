import React, { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
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
  onAfterSaveSchema: () => void;
  onCloseModal: () => void;
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
  onCloseModal,
  onSubmitModal
}) => {
  const [saved, setSaved] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const {
    updateConnection,
    deleteConnection,
    resetConnection
  } = useConnection();

  const schedule = FrequencyConfig.find(item =>
    equal(connection.schedule, item.config)
  );

  const onSubmit = async (values: {
    frequency: string;
    schema: SyncSchema;
  }) => {
    const frequencyData = FrequencyConfig.find(
      item => item.value === values.frequency
    );
    const initialSyncSchema = connection.syncSchema;

    const result = await updateConnection({
      connectionId: connection.connectionId,
      syncSchema: values.schema,
      status: connection.status,
      schedule: frequencyData?.config || null
    });

    if (result.status === "failure") {
      setErrorMessage(result.message);
    } else {
      setSaved(true);
      if (!equal(values.schema, initialSyncSchema)) {
        onAfterSaveSchema();
      }
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
          onSubmit={onSubmit}
          onReset={onReset}
          frequencyValue={schedule?.value}
          errorMessage={errorMessage}
          successMessage={saved && <FormattedMessage id="form.changesSaved" />}
        />
      </ContentCard>
      <DeleteBlock type="connection" onDelete={onDelete} />
      {isModalOpen ? (
        <ResetDataModal
          onClose={onCloseModal}
          onSubmit={onSubmitModal}
          modalType={ModalTypes.UPDATE_SCHEMA}
        />
      ) : null}
    </Content>
  );
};

export default SettingsView;
