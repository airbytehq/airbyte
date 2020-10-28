import React, { useCallback } from "react";
import { Field, FieldProps } from "formik";
import { FormattedHTMLMessage, FormattedMessage, useIntl } from "react-intl";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import { propertiesType } from "../../../core/resources/SourceSpecification";
import LabeledToggle from "../../LabeledToggle";

type IProps = {
  condition: propertiesType;
  property: string;
  setFieldValue: (field: string, value: string) => void;
};

const PropertyField: React.FC<IProps> = ({
  property,
  condition,
  setFieldValue
}) => {
  const formatMessage = useIntl().formatMessage;

  const onSetValue = useCallback(
    selectedItem => setFieldValue(property, selectedItem.value),
    [property, setFieldValue]
  );

  if (condition.type === "boolean") {
    return (
      <Field name={property}>
        {({ field }: FieldProps<string>) => (
          <LabeledToggle
            {...field}
            label={
              condition.title || (
                <FormattedMessage
                  id={`form.${property}`}
                  defaultMessage={property}
                />
              )
            }
            message={
              <FormattedHTMLMessage
                id="1"
                defaultMessage={condition.description}
              />
            }
            placeholder={condition.examples?.[0]}
          />
        )}
      </Field>
    );
  }

  if (condition.enum) {
    return (
      <Field name={property}>
        {({ field }: FieldProps<string>) => (
          <LabeledDropDown
            {...field}
            label={
              condition.title || (
                <FormattedMessage
                  id={`form.${property}`}
                  defaultMessage={property}
                />
              )
            }
            message={
              condition.description ? (
                <FormattedHTMLMessage
                  id="1"
                  defaultMessage={condition.description}
                />
              ) : null
            }
            placeholder={condition.examples?.[0]}
            filterPlaceholder={formatMessage({
              id: "form.searchName"
            })}
            data={condition.enum.map((dataItem: string) => ({
              text: dataItem,
              value: dataItem
            }))}
            onSelect={onSetValue}
          />
        )}
      </Field>
    );
  }

  return (
    <Field name={property}>
      {({ field }: FieldProps<string>) => (
        <LabeledInput
          {...field}
          autoComplete="off"
          label={
            condition.title || (
              <FormattedMessage
                id={`form.${property}`}
                defaultMessage={property}
              />
            )
          }
          message={
            condition.description ? (
              <FormattedHTMLMessage
                id="1"
                defaultMessage={condition.description}
              />
            ) : null
          }
          placeholder={condition.examples?.[0]}
          type={condition.type === "integer" ? "number" : "text"}
        />
      )}
    </Field>
  );
};

export default PropertyField;
