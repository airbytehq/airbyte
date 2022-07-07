import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal } from "components";

import useRequestConnector from "hooks/services/useRequestConnector";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import ConnectorForm from "./components/ConnectorForm";
import { Values } from "./types";

interface RequestConnectorModalProps {
  onClose: () => void;
  connectorType: "source" | "destination";
  initialName?: string;
}
const Content = styled.div`
  width: 492px;
  padding: 22px 34px 36px 32px;
`;

const RequestConnectorModal: React.FC<RequestConnectorModalProps> = ({ onClose, connectorType, initialName }) => {
  const [hasFeedback, setHasFeedback] = useState(false);
  const { requestConnector } = useRequestConnector();
  const workspace = useCurrentWorkspace();
  const onSubmit = (values: Values) => {
    requestConnector(values);
    setHasFeedback(true);

    setTimeout(() => {
      setHasFeedback(false);
      onClose();
    }, 2000);
  };

  return (
    <Modal title={<FormattedMessage id="connector.requestConnector" />} onClose={onClose}>
      <Content>
        <ConnectorForm
          onSubmit={onSubmit}
          onCancel={onClose}
          currentValues={{
            connectorType,
            name: initialName ?? "",
            additionalInfo: "",
            email: workspace.email,
          }}
          hasFeedback={hasFeedback}
        />
      </Content>
    </Modal>
  );
};

export default RequestConnectorModal;
