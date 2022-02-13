import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, Button, LabeledToggle } from "components";
import { getIcon } from "utils/imageUtils";

type ConnectorItem = {
  name?: string;
  stage?: string;
  icon?: string;
};

type AcknowledgementOfTermsModalProps = {
  onClose: () => void;
  onSubmit: () => void;
  connector: ConnectorItem;
};

const Content = styled.div`
  max-width: 430px;
  padding: 15px 20px 21px;
  font-style: normal;
  font-size: 14px;
  line-height: 17px;
  text-transform: capitalize;
`;

const Title = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CheckBoxContainer = styled.div`
  display: flex;
  align-items: center;
  margin-top: 21px;
`;

const Agreement = styled(LabeledToggle)`
  & label {
    font-size: 11px;
  }
`;

const Footer = styled.div`
  padding: 15px 20px;
  border-top: 1px solid ${({ theme }) => theme.greyColor30};
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;

const CancelButton = styled(Button)`
  margin-right: 10px;
`;

const Stage = styled.div`
  padding: 2px 6px;
  height: 14px;
  background: ${({ theme }) => theme.greyColor20};
  border-radius: 25px;
  text-transform: uppercase;
  font-weight: 500;
  font-size: 8px;
  line-height: 10px;
  color: ${({ theme }) => theme.textColor};
`;

const Icon = styled.div`
  width: 27px;
  margin-right: 12px;
  display: inline-block;

  & img {
    vertical-align: middle;
  }
`;

const ModalTitle: React.FC<ConnectorItem> = (props) => {
  return (
    <Title>
      <div>
        {props.icon && <Icon>{getIcon(props.icon)}</Icon>}
        {props.name}
      </div>
      <Stage>{props.stage}</Stage>
    </Title>
  );
};

const AcknowledgementOfTermsModal: React.FC<AcknowledgementOfTermsModalProps> = ({
  onClose,
  onSubmit,
  connector,
}) => {
  const [agreed, setAgreed] = useState(false);

  return (
    <Modal
      title={
        <ModalTitle
          name={connector.name}
          stage={connector.stage}
          icon={connector.icon}
        />
      }
      onClose={onClose}
    >
      <>
        <Content>
          <FormattedMessage
            id="connector.termsModal.text"
            values={{
              b: (...b: React.ReactNode[]) => <strong>{b}</strong>,
              br: <br />,
            }}
          />

          <CheckBoxContainer>
            <Agreement
              checkbox
              checked={agreed}
              onChange={() => setAgreed(!agreed)}
              label={<FormattedMessage id="connector.acknowledgeTerms" />}
            />
          </CheckBoxContainer>
        </Content>
        <Footer>
          <CancelButton secondary onClick={onClose}>
            <FormattedMessage id="form.cancel" />
          </CancelButton>
          <Button onClick={onSubmit} disabled={!agreed}>
            <FormattedMessage id="form.continue" />
          </Button>
        </Footer>
      </>
    </Modal>
  );
};

export default AcknowledgementOfTermsModal;
