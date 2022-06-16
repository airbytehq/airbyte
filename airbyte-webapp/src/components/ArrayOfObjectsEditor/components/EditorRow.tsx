import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import ToolTip from "components/ToolTip";

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

const DeleteButton = styled(Button)`
  margin-left: 7px;
`;

interface EditorRowProps {
  name?: React.ReactNode;
  description?: React.ReactNode;
  id: number;
  onEdit: (id: number) => void;
  onRemove: (id: number) => void;
  disabled?: boolean;
}

const EditorRow: React.FC<EditorRowProps> = ({ name, id, description, onEdit, onRemove, disabled }) => {
  const { formatMessage } = useIntl();
  const buttonLabel = formatMessage({ id: "form.delete" });

  const row = (
    <Content>
      <div>{name || id}</div>
      <div>
        <Button secondary onClick={() => onEdit(id)} type="button" disabled={disabled}>
          <FormattedMessage id="form.edit" />
        </Button>
        <DeleteButton iconOnly onClick={() => onRemove(id)} disabled={disabled} aria-label={buttonLabel}>
          <FontAwesomeIcon icon={faTimes} />
        </DeleteButton>
      </div>
    </Content>
  );

  return description ? <ToolTip control={row}>{description}</ToolTip> : row;
};

export { EditorRow };
