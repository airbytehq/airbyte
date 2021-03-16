import React from "react";
import { useIntl } from "react-intl";
import { useField } from "formik";

import { DropDown, Input, TextArea, Multiselect } from "components";
import ConfirmationControl from "./ConfirmationControl";
import { FormBaseItem } from "core/form/types";
import TagInput from "../../../base/TagInput/TagInput";

type IProps = {
  property: FormBaseItem;
  name: string;
  unfinishedFlows: Record<string, { startValue: string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
};

const Control: React.FC<IProps> = ({
  property,
  name,
  addUnfinishedFlow,
  removeUnfinishedFlow,
  unfinishedFlows,
}) => {
  const formatMessage = useIntl().formatMessage;
  const [field, meta, form] = useField(name);

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

  if (property.type === "array" && property.enum) {
    return (
      <Multiselect
        {...field}
        allowCreate={true}
        placeholder={placeholder}
        data={property.enum as string[]}
      />
    );
  }

  if (property.type === "array" && !property.enum) {
    return (
      <TagInput
        inputProps={{
          ...field,
          placeholder: formatMessage({
            id: "welcome.inviteEmail.placeholder",
          }),
          onChange: (props) => {
            field.onChange(props);
          },
        }}
        value={[{ id: "1", value: "test" }]}
        onEnter={() => {
          // addTag(value);
          // resetForm({});
        }}
        onDelete={
          () => ({})
          // onError={() =>
          // setFieldError(
          //   "newEmail",
          //   formatMessage({
          //     id: "form.email.error",
          //   })
          // )
        }
        // addOnBlur
        // error={meta.error}
      />
    );
  }

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
    const unfinishedSecret = unfinishedFlows[name];
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
        onDone={() => removeUnfinishedFlow(name)}
        onStart={() => {
          addUnfinishedFlow(name, { startValue: field.value });
          form.setValue("");
        }}
        onCancel={() => {
          removeUnfinishedFlow(name);
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
    const inputType = property.type === "integer" ? "number" : "text";

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
