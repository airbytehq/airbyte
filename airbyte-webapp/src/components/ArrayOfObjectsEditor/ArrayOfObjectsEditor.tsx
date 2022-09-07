import React from "react";
import { FormattedMessage } from "react-intl";

import Modal, { ModalProps } from "components/Modal";

import { ConnectionFormMode } from "views/Connection/ConnectionForm/ConnectionForm";

import styles from "./ArrayOfObjectsEditor.module.scss";
import { EditorHeader } from "./components/EditorHeader";
import { EditorRow } from "./components/EditorRow";

interface ItemBase {
  name?: string;
  description?: string;
}

export interface ArrayOfObjectsEditorProps<T extends ItemBase> {
  items: T[];
  editableItemIndex?: number | string | null;
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  renderItemName?: (item: T, index: number) => React.ReactNode | undefined;
  renderItemDescription?: (item: T, index: number) => React.ReactNode | undefined;
  renderItemEditorForm: (item?: T) => React.ReactNode;
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
  renderItemEditorForm,
  items,
  editableItemIndex,
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
      <Modal
        title={<FormattedMessage id={item ? "form.edit" : "form.add"} />}
        size={editModalSize}
        testId="arrayOfObjects-editModal"
      >
        {renderItemEditorForm(item)}
      </Modal>
    );
  };

  return (
    <>
      <div className={styles.container}>
        <EditorHeader
          itemsCount={items.length}
          onAddItem={onAddItem}
          mainTitle={mainTitle}
          addButtonText={addButtonText}
          mode={mode}
          disabled={disabled}
        />
        {items.length ? (
          <div className={styles.list}>
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
          </div>
        ) : null}
      </div>
      {mode !== "readonly" && isEditable && renderEditModal()}
    </>
  );
};
