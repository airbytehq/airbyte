import { ArrayHelpers, FormikProps } from "formik";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";

import { OperationCreate, OperationRead } from "core/request/AirbyteClient";
import { isDefined } from "utils/common";
import TransformationForm from "views/Connection/TransformationForm";

import { ConnectionFormMode } from "../ConnectionForm";

interface TransformationFieldProps extends ArrayHelpers {
  form: FormikProps<{ transformations: OperationRead[] }>;
  defaultTransformation: OperationCreate;
  mode?: ConnectionFormMode;
  onStartEdit?: () => void;
  onEndEdit?: () => void;
}

const TransformationField: React.FC<TransformationFieldProps> = ({
  remove,
  push,
  replace,
  form,
  defaultTransformation,
  mode,
  onStartEdit,
  onEndEdit,
}) => {
  const [editableItemIdx, setEditableItem] = useState<number | null>(null);

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
      mode={mode}
      editModalSize="xl"
      renderItemEditorForm={(editableItem) => (
        <TransformationForm
          transformation={editableItem ?? defaultTransformation}
          isNewTransformation={!editableItem}
          onCancel={() => {
            setEditableItem(null);
            onEndEdit?.();
          }}
          onDone={(transformation) => {
            if (isDefined(editableItemIdx)) {
              editableItemIdx >= form.values.transformations.length
                ? push(transformation)
                : replace(editableItemIdx, transformation);
              setEditableItem(null);
              onEndEdit?.();
            }
          }}
        />
      )}
    />
  );
};

export { TransformationField };
