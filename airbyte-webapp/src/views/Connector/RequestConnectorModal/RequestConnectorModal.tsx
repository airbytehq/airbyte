import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import ConnectorForm from "./components/ConnectorForm";

import { Modal } from "components";
import useRequestConnector from "components/hooks/services/useRequestConnector";
import useWorkspace from "components/hooks/services/useWorkspaceHook";
import { Values } from "./types";

type RequestConnectorModalProps = {
  onClose: () => void;
  connectorType: "source" | "destination";
};
const Content = styled.div`
  width: 492px;
  padding: 22px 34px 36px 32px;
`;

const RequestConnectorModal: React.FC<RequestConnectorModalProps> = ({
  onClose,
  connectorType,
}) => {
  const { requestConnector } = useRequestConnector();
  const { workspace } = useWorkspace();

  const onSubmit = (values: Values) => {
    requestConnector(values);
    onClose();
  };

  return (
    <Modal
      title={<FormattedMessage id="connector.requestConnector" />}
      onClose={onClose}
    >
      <Content>
        <ConnectorForm
          onSubmit={onSubmit}
          onCancel={onClose}
          currentValues={{
            connectorType: connectorType,
            name: "",
            website: "",
            email: workspace.email,
          }}
        />
      </Content>
    </Modal>
  );
};

export default RequestConnectorModal;
