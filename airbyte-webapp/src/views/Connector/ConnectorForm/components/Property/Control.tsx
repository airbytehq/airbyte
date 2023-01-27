import { Field, useField } from "formik";
import React, { useCallback } from "react";

import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { Multiselect } from "components/ui/Multiselect";
import { TagInput } from "components/ui/TagInput/TagInput";
import { TextArea } from "components/ui/TextArea";

import { FormBaseItem } from "core/form/types";
import { useExperiment } from "hooks/services/Experiment";
import { isDefined } from "utils/common";

import SecretConfirmationControl from "./SecretConfirmationControl";

const DatePicker = React.lazy(() => import("components/ui/DatePicker"));

interface ControlProps {
  property: FormBaseItem;
  name: string;
  disabled?: boolean;
  error?: boolean;
}

export const Control: React.FC<ControlProps> = ({ property, name, disabled, error }) => {
  const [field, meta, helpers] = useField(name);
  const useDatepickerExperiment = useExperiment("connector.form.useDatepicker", true);

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      field.onChange(e);
      if (!property.default && e.target.value === "") {
        // in case the input is not required and the user deleted their value, reset to undefined to avoid sending
        // an empty string which might fail connector validation.
        // Do not do this if there's a default value, formik will fill it in when casting.
        helpers.setValue(undefined);
      }
    },
    [field, helpers, property.default]
  );

  if (property.type === "array" && !property.enum) {
    return (
      <Field name={name} defaultValue={property.default || []}>
        {() => (
          <TagInput
            name={name}
            fieldValue={field.value || []}
            onChange={(tagLabels) => helpers.setValue(tagLabels)}
            error={!!meta.error}
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

  if (
    property.type === "string" &&
    (property.format === "date-time" || property.format === "date") &&
    useDatepickerExperiment
  ) {
    return (
      <DatePicker
        error={error}
        withTime={property.format === "date-time"}
        onChange={(value) => {
          helpers.setTouched(true);
          if (!property.default && value === "") {
            // in case the input is not required and the user deleted their value, reset to undefined to avoid sending
            // an empty string which might fail connector validation.
            // Do not do this if there's a default value, formik will fill it in when casting.
            helpers.setValue(undefined);
          } else {
            helpers.setValue(value);
          }
        }}
        value={field.value}
        disabled={disabled}
        onBlur={() => helpers.setTouched(true)}
      />
    );
  }

  const value = field.value;
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
    return (
      <TextArea
        {...field}
        onChange={onChange}
        autoComplete="off"
        value={value ?? ""}
        rows={3}
        disabled={disabled}
        error={error}
      />
    );
  } else if (property.isSecret) {
    const isFormInEditMode = isDefined(meta.initialValue);
    return (
      <SecretConfirmationControl
        name={name}
        multiline={Boolean(property.multiline)}
        showButtons={isFormInEditMode}
        disabled={disabled}
        error={error}
        onChange={onChange}
      />
    );
  }
  const inputType = property.type === "integer" || property.type === "number" ? "number" : "text";

  return (
    <Input
      {...field}
      onChange={onChange}
      placeholder={inputType === "number" ? property.default?.toString() : undefined}
      autoComplete="off"
      type={inputType}
      value={value ?? ""}
      disabled={disabled}
      error={error}
    />
  );
};
