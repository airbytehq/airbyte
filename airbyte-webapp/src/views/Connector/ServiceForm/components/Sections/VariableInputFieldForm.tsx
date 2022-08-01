import { useField } from "formik";
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
  const hiddenPath = `__variableInputField`;
  const [field, , fieldHelper] = useField(hiddenPath);
  const { validationSchema } = useServiceForm();

  const { value: isValid } = useAsync(
    async (): Promise<boolean> => yup.reach(validationSchema, path).isValid(field.value),
    [field.value, path, validationSchema]
  );

  useEffectOnce(() => {
    // Find initial values if not editing item
    const initialValue = item
      ? {}
      : (formField.properties as FormGroupItem).properties.reduce((acc, item) => {
          if (item._type === "formItem" && item.default) {
            acc[item.fieldKey] = item.default;
          }

          return acc;
        }, {} as Record<string, unknown>);

    fieldHelper.setValue(item ?? initialValue);
  });

  return (
    <>
      <ModalBody maxHeight={300}>
        <FormSection blocks={formField.properties} path={hiddenPath} disabled={disabled} skipAppend />
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
