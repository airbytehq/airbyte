import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";

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

type ArrayOfObjectsEditorProps = {
  items: { name: string }[];
  children?: React.ReactNode;
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  doneButtonText?: React.ReactNode;
  onStartEdit: (n: number) => void;
  onCancelEdit: () => void;
  onDone: () => void;
  onRemove: (index: number) => void;
  isEditMode: boolean;
};

const ArrayOfObjectsEditor: React.FC<ArrayOfObjectsEditorProps> = ({
  onStartEdit,
  onDone,
  onRemove,
  onCancelEdit,
  isEditMode,
  items,
  children,
  mainTitle,
  addButtonText,
  doneButtonText,
}) => {
  const onAddItem = React.useCallback(() => onStartEdit(items.length), [
    onStartEdit,
    items,
  ]);
  const handleRemove = React.useCallback((idx: number) => onRemove(idx), [
    onRemove,
    items,
  ]);
  const handleEdit = React.useCallback((idx: number) => onStartEdit(idx), [
    onStartEdit,
    items,
  ]);

  if (isEditMode) {
    return (
      <Content>
        {typeof children === "function" ? children() : children}
        <ButtonContainer>
          <SmallButton onClick={onCancelEdit} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </SmallButton>
          <SmallButton
            onClick={onDone}
            type="button"
            data-test-id="done-button"
          >
            {doneButtonText || <FormattedMessage id="form.done" />}
          </SmallButton>
        </ButtonContainer>
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
      />
      {items.length ? (
        <ItemsList>
          {items.map((item, key) => (
            <EditorRow
              key={`form-item-${key}`}
              name={item.name}
              id={key}
              onEdit={handleEdit}
              onRemove={handleRemove}
            />
          ))}
        </ItemsList>
      ) : null}
    </Content>
  );
};

export { ArrayOfObjectsEditor };
export type { ArrayOfObjectsEditorProps };
