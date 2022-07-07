import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";

import { EditorHeader } from "./components/EditorHeader";
import { EditorRow } from "./components/EditorRow";

const ItemsList = styled.div`
  background: ${({ theme }) => theme.greyColor0};
  border-radius: 4px;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const SmallButton = styled(Button)`
  margin-left: 8px;
  padding: 6px 8px 7px;
`;

const Content = styled.div`
  margin-bottom: 20px;
`;

export interface ArrayOfObjectsEditorProps<T extends { name: string }> {
  items: T[];
  editableItemIndex?: number | string | null;
  children: (item?: T) => React.ReactNode;
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  onStartEdit: (n: number) => void;
  onCancelEdit?: () => void;
  onDone?: () => void;
  onRemove: (index: number) => void;
  mode?: ConnectionFormMode;
  disabled?: boolean;
}

export const ArrayOfObjectsEditor = <T extends { name: string } = { name: string }>({
  onStartEdit,
  onDone,
  onRemove,
  onCancelEdit,
  items,
  editableItemIndex,
  children,
  mainTitle,
  addButtonText,
  mode,
  disabled,
}: ArrayOfObjectsEditorProps<T>): JSX.Element => {
  const onAddItem = React.useCallback(() => onStartEdit(items.length), [onStartEdit, items]);

  const isEditable = editableItemIndex !== null && editableItemIndex !== undefined;

  if (mode !== "readonly" && isEditable) {
    const item = typeof editableItemIndex === "number" ? items[editableItemIndex] : undefined;
    return (
      <Content>
        {children(item)}
        {onCancelEdit || onDone ? (
          <ButtonContainer>
            {onCancelEdit && (
              <SmallButton onClick={onCancelEdit} type="button" secondary disabled={disabled}>
                <FormattedMessage id="form.cancel" />
              </SmallButton>
            )}
            {onDone && (
              <SmallButton onClick={onDone} type="button" data-testid="done-button" disabled={disabled}>
                <FormattedMessage id="form.done" />
              </SmallButton>
            )}
          </ButtonContainer>
        ) : null}
      </Content>
    );
  }

  return (
    <Content>
      <EditorHeader
        itemsCount={items.length}
        onAddItem={onAddItem}
        mainTitle={mainTitle}
        addButtonText={addButtonText}
        mode={mode}
        disabled={disabled}
      />
      {items.length ? (
        <ItemsList>
          {items.map((item, key) => (
            <EditorRow
              key={`form-item-${key}`}
              name={item.name}
              id={key}
              onEdit={onStartEdit}
              onRemove={onRemove}
              disabled={disabled}
            />
          ))}
        </ItemsList>
      ) : null}
    </Content>
  );
};
