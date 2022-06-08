import { ArrayHelpers, FormikProps } from "formik";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import ArrayOfObjectsEditor from "components/ArrayOfObjectsEditor";

import { OperationCreate, OperationRead } from "core/request/AirbyteClient";
import { isDefined } from "utils/common";
import TransformationForm from "views/Connection/TransformationForm";

import { ConnectionFormMode } from "../ConnectionForm";

const TransformationField: React.FC<
  ArrayHelpers & {
    form: FormikProps<{ transformations: OperationRead[] }>;
    defaultTransformation: OperationCreate;
    mode?: ConnectionFormMode;
  }
> = ({ remove, push, replace, form, defaultTransformation, mode }) => {
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
      onStartEdit={(idx) => setEditableItem(idx)}
      mode={mode}
    >
      {(editableItem) => (
        <TransformationForm
          transformation={editableItem ?? defaultTransformation}
          isNewTransformation={!editableItem}
          onCancel={() => setEditableItem(null)}
          onDone={(transformation) => {
            if (isDefined(editableItemIdx)) {
              editableItemIdx >= form.values.transformations.length
                ? push(transformation)
                : replace(editableItemIdx, transformation);
              setEditableItem(null);
            }
          }}
        />
      )}
    </ArrayOfObjectsEditor>
  );
};

export { TransformationField };
