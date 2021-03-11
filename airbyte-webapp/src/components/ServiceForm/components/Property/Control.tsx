import React from "react";
import { useIntl } from "react-intl";
import { useField } from "formik";

import { DropDown, Input, TextArea } from "components";
import ConfirmationControl from "./ConfirmationControl";
import { FormBaseItem } from "core/form/types";

type IProps = {
  property: FormBaseItem;
  unfinishedSecrets: Record<string, { startValue: string }>;
  addUnfinishedSecret: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedSecret: (key: string) => void;
};

const Control: React.FC<IProps> = ({
  property,
  addUnfinishedSecret,
  removeUnfinishedSecret,
  unfinishedSecrets,
}) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName } = property;
  const [field, meta, form] = useField(fieldName);

  // TODO: think what to do with other cases
  let placeholder: string | undefined;

  switch (typeof property.examples) {
    case "object":
      if (Array.isArray(property.examples)) {
        placeholder = property.examples[0] + "";
      }
      break;
    case "number":
      placeholder = `${property.examples}`;
      break;
    case "string":
      placeholder = property.examples;
      break;
  }

  const value = field.value ?? property.default;

  if (property.enum) {
    return (
      <DropDown
        {...field}
        placeholder={placeholder}
        filterPlaceholder={formatMessage({
          id: "form.searchName",
        })}
        data={property.enum.map((dataItem) => ({
          text: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? "",
        }))}
        onSelect={(selectedItem) => form.setValue(selectedItem.value)}
        value={value}
      />
    );
  } else if (property.multiline && !property.isSecret) {
    return (
      <TextArea
        {...field}
        placeholder={placeholder}
        autoComplete="off"
        value={value ?? ""}
        rows={3}
      />
    );
  } else if (property.isSecret) {
    const unfinishedSecret = unfinishedSecrets[fieldName];
    const isEditInProgress = !!unfinishedSecret;
    const isFormInEditMode = !!meta.initialValue;
    return (
      <ConfirmationControl
        component={
          property.multiline && (isEditInProgress || !isFormInEditMode) ? (
            <TextArea
              {...field}
              autoComplete="off"
              placeholder={placeholder}
              value={value ?? ""}
              rows={3}
            />
          ) : (
            <Input
              {...field}
              autoComplete="off"
              placeholder={placeholder}
              value={value ?? ""}
              type="password"
            />
          )
        }
        showButtons={isFormInEditMode}
        isEditInProgress={isEditInProgress}
        onDone={() => removeUnfinishedSecret(fieldName)}
        onStart={() => {
          addUnfinishedSecret(fieldName, { startValue: field.value });
          form.setValue("");
        }}
        onCancel={() => {
          removeUnfinishedSecret(fieldName);
          if (
            unfinishedSecret &&
            unfinishedSecret.hasOwnProperty("startValue")
          ) {
            form.setValue(unfinishedSecret.startValue);
          }
        }}
      />
    );
  } else {
    const inputType: string = property.type === "integer" ? "number" : "text";

    return (
      <Input
        {...field}
        placeholder={placeholder}
        autoComplete="off"
        type={inputType}
        value={value ?? ""}
      />
    );
  }
};

export { Control };
