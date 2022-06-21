import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Modal, { ModalProps } from "components/Modal";

import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";

import { EditorHeader } from "./components/EditorHeader";
import { EditorRow } from "./components/EditorRow";

const ItemsList = styled.div`
  background: ${({ theme }) => theme.grey50};
  border-radius: 4px;
`;

const Content = styled.div`
  margin-bottom: 20px;
`;

interface ItemBase {
  name?: string;
  description?: string;
}

export interface ArrayOfObjectsEditorProps<T extends ItemBase> {
  items: T[];
  editableItemIndex?: number | string | null;
  children: (item?: T) => React.ReactNode;
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  renderItemName?: (item: T, index: number) => React.ReactNode | undefined;
  renderItemDescription?: (item: T, index: number) => React.ReactNode | undefined;
  onStartEdit: (n: number) => void;
  onRemove: (index: number) => void;
  mode?: ConnectionFormMode;
  disabled?: boolean;
  editModalSize?: ModalProps["size"];
}

export const ArrayOfObjectsEditor = <T extends ItemBase = ItemBase>({
  onStartEdit,
  onRemove,
  renderItemName = (item) => item.name,
  renderItemDescription = (item) => item.description,
  items,
  editableItemIndex,
  children,
  mainTitle,
  addButtonText,
  mode,
  disabled,
  editModalSize,
}: ArrayOfObjectsEditorProps<T>): JSX.Element => {
  const onAddItem = React.useCallback(() => onStartEdit(items.length), [onStartEdit, items]);
  const isEditable = editableItemIndex !== null && editableItemIndex !== undefined;

  const renderEditModal = () => {
    const item = typeof editableItemIndex === "number" ? items[editableItemIndex] : undefined;

    return (
      <Modal title={<FormattedMessage id="form.add" />} size={editModalSize}>
        {children(item)}
      </Modal>
    );
  };

  return (
    <>
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
            {items.map((item, index) => (
              <EditorRow
                key={`form-item-${index}`}
                name={renderItemName(item, index)}
                description={renderItemDescription(item, index)}
                id={index}
                onEdit={onStartEdit}
                onRemove={onRemove}
                disabled={disabled}
              />
            ))}
          </ItemsList>
        ) : null}
      </Content>
      {mode !== "readonly" && isEditable && renderEditModal()}
    </>
  );
};
