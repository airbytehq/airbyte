import React, { useCallback } from "react";
import { useFormContext } from "react-hook-form";

import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { Multiselect } from "components/ui/Multiselect";
import { TagInput } from "components/ui/TagInput/TagInput";
import { TextArea } from "components/ui/TextArea";

import { FormBaseItem } from "core/form/types";
import { useExperiment } from "hooks/services/Experiment";

import SecretConfirmationControl from "./SecretConfirmationControl";

const DatePicker = React.lazy(() => import("components/ui/DatePicker"));

interface ControlProps {
  property: FormBaseItem;
  name: string;
  disabled?: boolean;
  error?: boolean;
}

export const Control: React.FC<ControlProps> = ({ property, name, disabled, error }) => {
  const { register, setValue, watch, formState, getFieldState } = useFormContext();
  const fieldValue = watch(name);
  console.log(name, fieldValue);
  const fieldState = getFieldState("firstName", formState); // It is subscribed now and reactive to error state updated
  // const [field, meta, helpers] = useField(name);
  const useDatepickerExperiment = useExperiment("connector.form.useDatepicker", true);

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      if (!property.default && e.target.value === "") {
        // in case the input is not required and the user deleted their value, reset to undefined to avoid sending
        // an empty string which might fail connector validation.
        // Do not do this if there's a default value, formik will fill it in when casting.
        setValue(name, undefined);
      } else {
        setValue(name, e.target.value);
      }
    },
    [name, property.default, setValue]
  );

  if (property.type === "array" && !property.enum) {
    return (
      <TagInput
        name={name}
        fieldValue={fieldValue || []}
        onChange={(tagLabels) => setValue(name, tagLabels)}
        error={!!fieldState.error}
        disabled={disabled}
      />
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
        onChange={(dataItems) => setValue(name, dataItems)}
        value={fieldValue}
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
          if (!property.default && value === "") {
            // in case the input is not required and the user deleted their value, reset to undefined to avoid sending
            // an empty string which might fail connector validation.
            // Do not do this if there's a default value, formik will fill it in when casting.
            setValue(name, undefined);
          } else {
            setValue(name, value);
          }
        }}
        value={fieldValue}
        disabled={disabled}
        onBlur={() => setValue(name, fieldValue)}
      />
    );
  }

  const value = fieldValue ?? property.default;
  if (property.enum) {
    return (
      <DropDown
        {...register(name)}
        options={property.enum.map((dataItem) => ({
          label: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? "",
        }))}
        onChange={(selectedItem) => selectedItem && setValue(name, selectedItem.value)}
        value={value}
        isDisabled={disabled}
        error={error}
      />
    );
  } else if (property.multiline && !property.isSecret) {
    return (
      <TextArea
        {...register(name)}
        onChange={onChange}
        autoComplete="off"
        value={value ?? ""}
        rows={3}
        disabled={disabled}
        error={error}
      />
    );
  } else if (property.isSecret) {
    const isFormInEditMode = fieldState.isDirty;
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
      {...register(name)}
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
