import React, { useState } from "react";
import styled from "styled-components";
import { useIntl, FormattedMessage } from "react-intl";

import Modal from "components/Modal";
import { Button, LabeledInput } from "components";

export type IProps = {
  name: string;
  type: "source" | "destination";
  onClose: () => void;
  onClone: (name: string) => void;
};

const Content = styled.div`
  padding: 18px 37px 28px;
  font-size: 14px;
  line-height: 28px;
  max-width: 585px;
`;
const ButtonContent = styled.div`
  padding-top: 27px;
  text-align: right;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const CloneModal: React.FC<IProps> = ({ onClose, type, name, onClone }) => {
  const { formatMessage } = useIntl();
  const [newName, setNewName] = useState(`${name} (Copy)`);

  const onSuccess = () => {
    onClose();
    onClone(newName);
  };

  return (
    <Modal
      onClose={onClose}
      title={formatMessage({
        id: `tables.new${type}Title`,
      })}
    >
      <Content>
        <LabeledInput
          label={<FormattedMessage id={`form.${type}Name.placeholder`} />}
          message={<FormattedMessage id={`tables.new${type}HelpText`} />}
          type="text"
          value={newName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            setNewName(e.currentTarget.value);
          }}
        />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary>
            <FormattedMessage id="form.cancel" />
          </ButtonWithMargin>
          <Button onClick={onSuccess}>
            <FormattedMessage id={`onboarding.${type}SetUp.buttonText`} />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default CloneModal;
