import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components/Button";

const Content = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  color: ${({ theme }) => theme.textColor};
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  margin: 5px 0;
`;

type FormHeaderProps = {
  itemsCount: number;
  onAddItem: () => void;
};

const FormHeader: React.FC<FormHeaderProps> = ({ itemsCount, onAddItem }) => {
  return (
    <Content>
      <FormattedMessage id="form.items" values={{ count: itemsCount }} />
      <Button secondary type="button" onClick={onAddItem}>
        <FormattedMessage id="form.addItems" />
      </Button>
    </Content>
  );
};

export default FormHeader;
