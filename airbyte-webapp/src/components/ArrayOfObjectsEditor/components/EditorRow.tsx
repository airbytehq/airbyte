import { faPencil, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import ToolTip from "components/ToolTip";

const Content = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  color: ${({ theme }) => theme.darkBlue};
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  padding: 5px 12px 6px 14px;
  border-bottom: 1px solid ${({ theme }) => theme.white};

  &:last-child {
    border-bottom: none;
  }
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

  const row = (
    <Content>
      <div>{name || id}</div>
      <div>
        <Button
          iconOnly
          arial-label={formatMessage({ id: "form.edit" })}
          onClick={() => onEdit(id)}
          disabled={disabled}
        >
          <FontAwesomeIcon icon={faPencil} fixedWidth />
        </Button>
        <Button
          iconOnly
          aria-label={formatMessage({ id: "form.delete" })}
          onClick={() => onRemove(id)}
          disabled={disabled}
        >
          <FontAwesomeIcon icon={faTimes} fixedWidth />
        </Button>
      </div>
    </Content>
  );

  return description ? <ToolTip control={row}>{description}</ToolTip> : row;
};

export { EditorRow };
