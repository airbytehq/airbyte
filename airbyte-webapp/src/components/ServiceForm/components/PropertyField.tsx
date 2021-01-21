import React, { useMemo } from "react";
import { useField } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import LabeledToggle from "../../LabeledToggle";
import TextWithHTML from "../../TextWithHTML";
import { FormBaseItem } from "../../../core/form/types";

type IProps = {
  property: FormBaseItem;
};

const PropertyField: React.FC<IProps> = ({ property }) => {
  const formatMessage = useIntl().formatMessage;
  const { fieldName, fieldKey } = property;
  const [field, meta, form] = useField(fieldName);

  const defaultLabel = formatMessage({
    id: `form.${fieldKey}`,
    defaultMessage: fieldKey
  });

  const label = `${property.title || defaultLabel}${
    property.isRequired ? " *" : ""
  }`;

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

  const displayError = !!meta.error && meta.touched;

  const constructMessage = useMemo(() => {
    const errorMessage =
      displayError && meta.error === "form.pattern.error" ? (
        <FormattedMessage
          id={meta.error}
          values={{ pattern: property.pattern }}
        />
      ) : null;

    const message = property.description ? (
      <TextWithHTML text={property.description} />
    ) : null;
    return (
      <>
        {message} {errorMessage}
      </>
    );
  }, [displayError, meta.error, property.description, property.pattern]);

  if (property.type === "boolean") {
    return (
      <LabeledToggle
        {...field}
        label={property.title || defaultLabel}
        message={<TextWithHTML text={property.description} />}
        placeholder={placeholder}
        value={field.value ?? property.default}
      />
    );
  } else if (property.enum) {
    return (
      <LabeledDropDown
        {...field}
        error={displayError}
        label={label}
        message={constructMessage}
        placeholder={placeholder}
        filterPlaceholder={formatMessage({
          id: "form.searchName"
        })}
        data={property.enum.map(dataItem => ({
          text: dataItem?.toString() ?? "",
          value: dataItem?.toString() ?? ""
        }))}
        onSelect={selectedItem => form.setValue(selectedItem.value)}
        value={field.value || property.default}
      />
    );
  } else {
    const inputType = property.isSecret
      ? "password"
      : property.type === "integer"
      ? "number"
      : "text";

    return (
      <LabeledInput
        {...field}
        error={displayError}
        autoComplete="off"
        label={label}
        message={constructMessage}
        placeholder={placeholder}
        type={inputType}
        value={field.value || property.default || ""}
        withEditButton={inputType === "password" && !!meta.initialValue}
        setValue={form.setValue}
      />
    );
  }
};

export default PropertyField;
