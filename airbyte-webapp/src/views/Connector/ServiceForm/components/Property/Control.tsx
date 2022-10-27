import { Field, useField } from "formik";
import React from "react";

import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { Multiselect } from "components/ui/Multiselect";
import { SecretTextArea } from "components/ui/SecretTextArea";
import { TagInput } from "components/ui/TagInput/TagInput";
import { TextArea } from "components/ui/TextArea";

import { FormBaseItem } from "core/form/types";
import { isDefined } from "utils/common";

import ConfirmationControl from "./ConfirmationControl";

interface ControlProps {
  property: FormBaseItem;
  name: string;
  unfinishedFlows: Record<string, { startValue: string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  disabled?: boolean;
  error?: boolean;
}

export const Control: React.FC<ControlProps> = ({
  property,
  name,
  addUnfinishedFlow,
  removeUnfinishedFlow,
  unfinishedFlows,
  disabled,
  error,
}) => {
  const [field, meta, helpers] = useField(name);

  if (property.type === "array" && !property.enum) {
    return (
      <Field name={name} defaultValue={property.default || []}>
        {() => (
          <TagInput
            name={name}
            fieldValue={field.value || []}
            onChange={(tagLabels) => helpers.setValue(tagLabels)}
            // error={!!meta.error}
            disabled={disabled}
          />
        )}
      </Field>
    );
  }

  if (property.type === "array" && property.enum) {
    const data =
      property.enum?.length && typeof property.enum[0] !== "object"
        ? (property.enum as string[] | number[])
        : undefined;
    return (
      <Multiselect
        name={name}
        data={data}
        onChange={(dataItems) => helpers.setValue(dataItems)}
        value={field.value}
        disabled={disabled}
      />
    );
  }

  const value = field.value ?? property.default;
  if (property.enum) {
    return (
      <DropDown
        {...field}
        options={property.enum.map((dataItem) => ({
          label: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? "",
        }))}
        onChange={(selectedItem) => selectedItem && helpers.setValue(selectedItem.value)}
        value={value}
        isDisabled={disabled}
        error={error}
      />
    );
  } else if (property.multiline && !property.isSecret) {
    return <TextArea {...field} autoComplete="off" value={value ?? ""} rows={3} disabled={disabled} error={error} />;
  } else if (property.isSecret) {
    const unfinishedSecret = unfinishedFlows[name];
    const isEditInProgress = !!unfinishedSecret;
    const isFormInEditMode = isDefined(meta.initialValue);
    return (
      <ConfirmationControl
        component={
          property.multiline && (isEditInProgress || !isFormInEditMode) ? (
            <SecretTextArea
              {...field}
              autoComplete="off"
              value={value ?? ""}
              rows={3}
              disabled={disabled}
              error={error}
            />
          ) : (
            <Input
              {...field}
              autoComplete="off"
              value={value ?? ""}
              type="password"
              disabled={disabled}
              error={error}
            />
          )
        }
        showButtons={isFormInEditMode}
        isEditInProgress={isEditInProgress}
        onDone={() => removeUnfinishedFlow(name)}
        onStart={() => {
          addUnfinishedFlow(name, { startValue: field.value });
          helpers.setValue("");
        }}
        onCancel={() => {
          removeUnfinishedFlow(name);
          if (unfinishedSecret && unfinishedSecret.hasOwnProperty("startValue")) {
            helpers.setValue(unfinishedSecret.startValue);
          }
        }}
        disabled={disabled}
      />
    );
  }
  const inputType = property.type === "integer" ? "number" : "text";

  return <Input {...field} autoComplete="off" type={inputType} value={value ?? ""} disabled={disabled} error={error} />;
};
