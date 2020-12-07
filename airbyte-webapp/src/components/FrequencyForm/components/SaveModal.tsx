import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Modal from "../../Modal";
import Button from "../../Button";

export type IProps = {
  onClose: () => void;
  onSubmit: (data: any) => void;
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

const SaveModal: React.FC<IProps> = ({ onClose, onSubmit }) => {
  return (
    <Modal onClose={onClose} title={<FormattedMessage id="form.resetData" />}>
      <Content>
        <FormattedMessage id="form.changedColumns" />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary>
            <FormattedMessage id="form.noNeed" />
          </ButtonWithMargin>
          <Button onClick={onSubmit}>
            <FormattedMessage id="form.reset" />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default SaveModal;
