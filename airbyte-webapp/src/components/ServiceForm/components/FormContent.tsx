import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import React from "react";
import styled from "styled-components";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import Instruction from "./Instruction";
import FrequencyConfig from "../../../data/FrequencyConfig.json";
import { specification } from "../../../core/resources/SourceSpecification";
import LabeledToggle from "../../LabeledToggle";

type IProps = {
  isEditMode?: boolean;
  dropDownData: Array<IDataItem>;
  setFieldValue: (item: any, value: any) => void;
  onDropDownSelect?: (id: string) => void;
  formType: "source" | "destination" | "connection";
  values: { name: string; serviceType: string; frequency?: string };
  specifications?: specification;
  properties?: Array<string>;
  documentation?: string;
};

const FormItem = styled.div`
  margin-bottom: 27px;
`;

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

const FormContent: React.FC<IProps> = ({
  dropDownData,
  formType,
  setFieldValue,
  values,
  isEditMode,
  onDropDownSelect,
  specifications,
  properties,
  documentation
}) => {
  const formatMessage = useIntl().formatMessage;
  const dropdownData = React.useMemo(
    () =>
      FrequencyConfig.map(item => ({
        ...item,
        text:
          item.value === "manual"
            ? item.text
            : formatMessage(
                {
                  id: "form.every"
                },
                {
                  value: item.text
                }
              )
      })),
    [formatMessage]
  );

  return (
    <>
      <FormItem>
        <Field name="name">
          {({ field }: FieldProps<string>) => (
            <LabeledInput
              {...field}
              label={<FormattedMessage id="form.name" />}
              placeholder={formatMessage({
                id: `form.${formType}Name.placeholder`
              })}
              type="text"
              message={formatMessage({
                id: `form.${formType}Name.message`
              })}
            />
          )}
        </Field>
      </FormItem>

      <FormItem>
        <Field name="serviceType">
          {({ field }: FieldProps<string>) => (
            <SmallLabeledDropDown
              {...field}
              disabled={isEditMode}
              label={formatMessage({
                id: `form.${formType}Type`
              })}
              hasFilter
              placeholder={formatMessage({
                id: "form.selectConnector"
              })}
              filterPlaceholder={formatMessage({
                id: "form.searchName"
              })}
              data={dropDownData}
              onSelect={item => {
                setFieldValue("serviceType", item.value);
                if (onDropDownSelect) {
                  onDropDownSelect(item.value);
                }
              }}
            />
          )}
        </Field>
        {values.serviceType && formType !== "connection" && (
          <Instruction
            serviceId={values.serviceType}
            dropDownData={dropDownData}
            url={documentation}
          />
        )}
      </FormItem>

      {properties?.map(item => {
        const condition = specifications?.properties[item];

        if (condition?.type === "boolean") {
          return (
            <FormItem key={`form-field-${item}`}>
              <Field name={item}>
                {({ field }: FieldProps<string>) => (
                  <LabeledToggle
                    {...field}
                    label={
                      condition.title || (
                        <FormattedMessage
                          id={`form.${item}`}
                          defaultMessage={item}
                        />
                      )
                    }
                    message={condition?.description}
                    placeholder={
                      condition?.examples?.length ? condition?.examples[0] : ""
                    }
                  />
                )}
              </Field>
            </FormItem>
          );
        }

        return (
          <FormItem key={`form-field-${item}`}>
            <Field name={item}>
              {({ field }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={
                    condition?.title || (
                      <FormattedMessage
                        id={`form.${item}`}
                        defaultMessage={item}
                      />
                    )
                  }
                  message={condition?.description}
                  placeholder={
                    condition?.examples?.length ? condition?.examples[0] : ""
                  }
                  type={condition?.type === "integer" ? "number" : "text"}
                />
              )}
            </Field>
          </FormItem>
        );
      })}

      {formType === "connection" && (
        <FormItem>
          <Field name="frequency">
            {({ field }: FieldProps<string>) => (
              <SmallLabeledDropDown
                {...field}
                labelAdditionLength={300}
                label={formatMessage({
                  id: "form.frequency"
                })}
                message={formatMessage({
                  id: "form.frequency.message"
                })}
                placeholder={formatMessage({
                  id: "form.frequency.placeholder"
                })}
                data={dropdownData}
                onSelect={item => setFieldValue("frequency", item.value)}
              />
            )}
          </Field>
        </FormItem>
      )}
    </>
  );
};

export default FormContent;
