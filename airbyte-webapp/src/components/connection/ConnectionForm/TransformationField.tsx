import { ArrayHelpers, FormikProps } from "formik";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";
import TransformationForm from "components/connection/TransformationForm";

import { OperationRead } from "core/request/AirbyteClient";
import { ConnectionFormMode } from "hooks/services/ConnectionForm/ConnectionFormService";
import { isDefined } from "utils/common";

import { useDefaultTransformation } from "./formConfig";

interface TransformationFieldProps extends ArrayHelpers {
  form: FormikProps<{ transformations: OperationRead[] }>;
  mode?: ConnectionFormMode;
  onStartEdit?: () => void;
  onEndEdit?: () => void;
}

const TransformationField: React.FC<TransformationFieldProps> = ({
  remove,
  push,
  replace,
  form,
  mode,
  onStartEdit,
  onEndEdit,
}) => {
  const [editableItemIdx, setEditableItem] = useState<number | null>(null);
  const defaultTransformation = useDefaultTransformation();
  const clearEditableItem = () => setEditableItem(null);

  return (
    <ArrayOfObjectsEditor
      items={form.values.transformations}
      editableItemIndex={editableItemIdx}
      mainTitle={
        <FormattedMessage id="form.transformationCount" values={{ count: form.values.transformations.length }} />
      }
      addButtonText={<FormattedMessage id="form.addTransformation" />}
      onRemove={remove}
      onStartEdit={(idx) => {
        setEditableItem(idx);
        onStartEdit?.();
      }}
      onCancel={() => {
        clearEditableItem();
        onEndEdit?.();
      }}
      mode={mode}
      editModalSize="xl"
      renderItemEditorForm={(editableItem) => (
        <TransformationForm
          transformation={editableItem ?? defaultTransformation}
          isNewTransformation={!editableItem}
          onCancel={() => {
            clearEditableItem();
            onEndEdit?.();
          }}
          onDone={(transformation) => {
            if (isDefined(editableItemIdx)) {
              editableItemIdx >= form.values.transformations.length
                ? push(transformation)
                : replace(editableItemIdx, transformation);
              clearEditableItem();
              onEndEdit?.();
            }
          }}
        />
      )}
    />
  );
};

export { TransformationField };
