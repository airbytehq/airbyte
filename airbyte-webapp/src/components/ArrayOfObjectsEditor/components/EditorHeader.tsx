import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";

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

type EditorHeaderProps = {
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  itemsCount: number;
  onAddItem: () => void;
  mode?: ConnectionFormMode;
};

const EditorHeader: React.FC<EditorHeaderProps> = ({ itemsCount, onAddItem, mainTitle, addButtonText, mode }) => {
  return (
    <Content>
      {mainTitle || <FormattedMessage id="form.items" values={{ count: itemsCount }} />}
      {mode !== "readonly" && (
        <Button secondary type="button" onClick={onAddItem} data-testid="addItemButton">
          {addButtonText || <FormattedMessage id="form.addItems" />}
        </Button>
      )}
    </Content>
  );
};

export { EditorHeader };
