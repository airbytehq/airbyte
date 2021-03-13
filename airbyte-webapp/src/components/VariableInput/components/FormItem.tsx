import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FormattedMessage } from "react-intl";

import Button from "../../Button";

const Content = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  color: ${({ theme }) => theme.textColor};
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  padding: 5px 12px 6px 14px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};

  &:last-child {
    border: none;
  }
`;

const Delete = styled(FontAwesomeIcon)`
  color: ${({ theme }) => theme.greyColor55};
  font-weight: 300;
  font-size: 14px;
  line-height: 24px;
  margin-left: 7px;
  cursor: pointer;
`;

type FormItemProps = {
  name: string;
  onEdit: () => void;
};

const FormItem: React.FC<FormItemProps> = ({ name, onEdit }) => {
  return (
    <Content>
      <div>{name}</div>
      <div>
        <Button secondary onClick={onEdit}>
          <FormattedMessage id="form.edit" />
        </Button>
        <Delete icon={faTimes} />
      </div>
    </Content>
  );
};

export default FormItem;
