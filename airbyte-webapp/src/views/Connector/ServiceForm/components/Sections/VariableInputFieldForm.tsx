import { useField } from "formik";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useAsync, useEffectOnce } from "react-use";
import * as yup from "yup";

import { Button, ModalBody, ModalFooter } from "components";

import { FormGroupItem, FormObjectArrayItem } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { FormSection } from "./FormSection";

interface VariableInputFormProps {
  formField: FormObjectArrayItem;
  path: string;
  item?: unknown;
  disabled?: boolean;
  onDone: (value: unknown) => void;
  onCancel: () => void;
}

export const VariableInputFieldForm: React.FC<VariableInputFormProps> = ({
  formField,
  path,
  item,
  disabled,
  onDone,
  onCancel,
}) => {
  // This form creates a temporary field for Formik to prevent the field from rendering in
  // the service form while it's being created or edited since it reuses the FormSection component.
  // The temp field is cleared when this form is done or canceled.
  const variableInputFieldPath = useMemo(() => `__temp__${path.replace(/\./g, "_").replace(/\[|\]/g, "")}`, [path]);
  const [field, , fieldHelper] = useField(variableInputFieldPath);
  const { validationSchema } = useServiceForm();

  // Copy the validation from the original field to ensure that the form has all the required values field out correctly.
  // One side effect of this is that validation errors will not be shown in this form because the validationSchema does not
  // contain info about the temp field.
  const { value: isValid } = useAsync(
    async (): Promise<boolean> => yup.reach(validationSchema, path).isValid(field.value),
    [field.value, path, validationSchema]
  );

  useEffectOnce(() => {
    const initialValue =
      item ??
      // Set initial default values when user is creating a new item
      (formField.properties as FormGroupItem).properties.reduce((acc, item) => {
        if (item._type === "formItem" && item.default) {
          // Only "formItem" types have a default value
          acc[item.fieldKey] = item.default;
        }

        return acc;
      }, {} as Record<string, unknown>);

    fieldHelper.setValue(initialValue);
  });

  return (
    <>
      <ModalBody maxHeight={300}>
        <FormSection blocks={formField.properties} path={variableInputFieldPath} disabled={disabled} skipAppend />
      </ModalBody>
      <ModalFooter>
        <Button
          data-testid="cancel-button"
          secondary
          onClick={() => {
            onCancel();
            fieldHelper.setValue(undefined, false);
          }}
        >
          <FormattedMessage id="form.cancel" />
        </Button>
        <Button
          data-testid="done-button"
          disabled={disabled || !isValid}
          onClick={() => {
            onDone(field.value);
            fieldHelper.setValue(undefined, false);
          }}
        >
          <FormattedMessage id="form.done" />
        </Button>
      </ModalFooter>
    </>
  );
};
