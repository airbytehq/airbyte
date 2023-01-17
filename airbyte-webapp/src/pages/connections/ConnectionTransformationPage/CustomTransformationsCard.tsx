import { FieldArray } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useToggle } from "react-use";

import { OperationCreate, OperationRead } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FormikOnSubmit } from "types/formik";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import { getInitialTransformations } from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";

export const CustomTransformationsCard: React.FC<{
  operations?: OperationCreate[];
  onSubmit: FormikOnSubmit<{ transformations?: OperationRead[] }>;
}> = ({ operations, onSubmit }) => {
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { mode } = useConnectionFormService();
  const initialValues = useMemo(
    () => ({
      transformations: getInitialTransformations(operations || []),
    }),
    [operations]
  );

  return (
    <FormCard<{ transformations?: OperationRead[] }>
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues,
        enableReinitialize: true,
        onSubmit,
      }}
      submitDisabled={editingTransformation}
    >
      <FieldArray name="transformations">
        {(formProps) => (
          <TransformationField
            {...formProps}
            mode={mode}
            onStartEdit={toggleEditingTransformation}
            onEndEdit={toggleEditingTransformation}
          />
        )}
      </FieldArray>
    </FormCard>
  );
};
