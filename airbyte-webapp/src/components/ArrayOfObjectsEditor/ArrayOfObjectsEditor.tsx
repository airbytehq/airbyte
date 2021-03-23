import React from "react";
import styled from "styled-components";

import { Button } from "components/Button";

import { EditorHeader } from "./components/EditorHeader";
import { EditorRow } from "./components/EditorRow";
import { FormattedMessage } from "react-intl";

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

type ArrayOfObjectsEditorProps = {
  items: { name: string }[];
  children?: React.ReactNode;
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
      <>
        {typeof children === "function" ? children() : children}
        <ButtonContainer>
          <SmallButton onClick={onCancelEdit} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </SmallButton>
          <SmallButton onClick={onDone} type="button">
            <FormattedMessage id="form.done" />
          </SmallButton>
        </ButtonContainer>
      </>
    );
  }

  return (
    <>
      <EditorHeader itemsCount={items.length} onAddItem={onAddItem} />
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
    </>
  );
};

export { ArrayOfObjectsEditor };
export type { ArrayOfObjectsEditorProps };
