import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Modal, Button, LabeledToggle } from "components";

type AcknowledgementOfTermsModalProps = {
  destinationDefinitionId?: string;
  onClose: () => void;
};

const Content = styled.div`
  max-width: 430px;
  padding: 15px 20px 21px;
  font-style: normal;
  font-size: 14px;
  line-height: 17px;
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
    line-height: 13px;
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

const Icon = styled.img`
  width: 27px;
  margin-right: 12px;
`;

const ModalTitle: React.FC<{ name: string; stage: string; img?: string }> = (
  props
) => {
  return (
    <Title>
      <div>
        {props.img && <Icon src={props.img} />}
        {props.name}
      </div>
      <Stage>{props.stage}</Stage>
    </Title>
  );
};

const AcknowledgementOfTermsModal: React.FC<AcknowledgementOfTermsModalProps> = ({
  onClose,
}) => {
  return (
    <Modal
      title={<ModalTitle name="Apple Store" stage="alpha" />}
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
              label={<FormattedMessage id="connector.acknowledgeTerms" />}
            />
          </CheckBoxContainer>
        </Content>
        <Footer>
          <CancelButton secondary>
            <FormattedMessage id="form.cancel" />
          </CancelButton>
          <Button disabled>
            <FormattedMessage id="form.continue" />
          </Button>
        </Footer>
      </>
    </Modal>
  );
};

export default AcknowledgementOfTermsModal;
