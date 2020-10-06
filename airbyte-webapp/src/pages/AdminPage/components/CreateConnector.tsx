import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import Button from "../../../components/Button";
import CreateConnectorModal from "./CreateConnectorModal";

const CreateConnector: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const onChangeModalState = () => setIsModalOpen(!isModalOpen);
  // TODO: add real onSubmit
  const onSubmit = () => null;

  return (
    <>
      <Button onClick={onChangeModalState}>
        <FormattedMessage id="admin.newConnector" />
      </Button>
      {isModalOpen && (
        <CreateConnectorModal
          onClose={onChangeModalState}
          onSubmit={onSubmit}
        />
      )}
    </>
  );
};

export default CreateConnector;
