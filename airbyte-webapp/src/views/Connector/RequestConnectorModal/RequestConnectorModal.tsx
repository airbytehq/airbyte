import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import ConnectorForm from "./components/ConnectorForm";

import { Modal } from "components";

const Content = styled.div`
  width: 492px;
  padding: 22px 34px 36px 32px;
`;

const RequestConnectorModal: React.FC = () => {
  return (
    <Modal title={<FormattedMessage id="connector.requestConnector" />}>
      <Content>
        <ConnectorForm />
      </Content>
    </Modal>
  );
};

export default RequestConnectorModal;
