// import { Field, FieldProps, Form, Formik } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl"; // useIntl
import styled from "styled-components";
// import * as yup from "yup";

import { DropDown } from "components"; // Button ,ControlLabels
// import { Card } from "components/base/Card";
import { ConnectorIcon } from "components/ConnectorIcon";

import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import { useDestinationList } from "../../../../../hooks/services/useDestinationHook";
import { useSourceList } from "../../../../../hooks/services/useSourceHook";

interface IProps {
  type: "source" | "destination";
  onSubmit: (id: string) => void;
  value: string;
  placeholder?: string;
}

// const FormContent = styled(Form)`
//   padding: 22px 27px 23px 0px;
// `;

const FormTitle = styled.div`
  font-size: 24px;
  line-height: 30px;
  color: #27272a;
  font-weight: 500;
  margin: 38px 0 20px 0;
`;

// const BottomBlock = styled.div`
//   text-align: right;
//   margin-top: 34px;
// `;

// const PaddingBlock = styled.div`
//   text-align: center;
//   padding: 18px 0 15px;
//   font-weight: 500;
//   font-size: 15px;
//   line-height: 18px;
// `;

// const existingEntityValidationSchema = yup.object().shape({
//   entityId: yup.string().required("form.empty.error"),
// });

const ExistingEntityForm: React.FC<IProps> = ({ type, onSubmit, value, placeholder }) => {
  // const { formatMessage } = useIntl();
  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinations } = useDestinationList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const dropDownData = useMemo(() => {
    if (type === "source") {
      return sources.map((item) => {
        const sourceDef = sourceDefinitions.find((sd) => sd.sourceDefinitionId === item.sourceDefinitionId);
        return {
          label: item.name,
          value: item.sourceId,
          img: <ConnectorIcon icon={sourceDef?.icon} />,
        };
      });
    }
    return destinations.map((item) => {
      const destinationDef = destinationDefinitions.find(
        (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
      );
      return {
        label: item.name,
        value: item.destinationId,
        img: <ConnectorIcon icon={destinationDef?.icon} />,
      };
    });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  if (!dropDownData.length) {
    return null;
  }

  // const initialValues = { entityId: value };
  return (
    <>
      {/* <Card title={<FormattedMessage id={`connectionForm.${type}Existing`} />}> */}
      <FormTitle>
        <FormattedMessage id={`form.select.existing.${type}`} />
      </FormTitle>

      {/*
      TODO: Anet => The Select Value cannot be reset outside the form, so the Formik component is deprecated.
      <Formik
        initialValues={initialValues}
        validationSchema={existingEntityValidationSchema}
        onSubmit={async (values: { entityId: string }, { resetForm }) => {
          onSubmit(values.entityId);
          resetForm({});
        }}
      >
        {(
          { setFieldValue } // isSubmitting
        ) => (
          <FormContent>
            <Field name="entityId">
              {({ field }: FieldProps<string>) => (
                <ControlLabels
                // label={formatMessage({
                //   id: `connectionForm.${type}Title`,
                // })}
                > */}
      <DropDown
        // {...field}
        $background="white"
        $withBorder
        value={value}
        // className={style.selectDropdown}
        options={dropDownData}
        placeholder={placeholder}
        onChange={(item: { value: string }) => {
          onSubmit(item.value);
          //  setFieldValue(field.name, item.value);
        }}
      />
      {/* </ControlLabels>
              )}
            </Field> */}
      {/* <BottomBlock>
                <Button disabled={isSubmitting} type="submit">
                  <FormattedMessage id={`connectionForm.${type}Use`} />
                </Button>
              </BottomBlock> */}
      {/* </FormContent>
        )}
      </Formik> */}
      {/* </Card> */}
      {/* <PaddingBlock> <FormattedMessage id="onboarding.or" /> </PaddingBlock>*/}
    </>
  );
};

export default ExistingEntityForm;
