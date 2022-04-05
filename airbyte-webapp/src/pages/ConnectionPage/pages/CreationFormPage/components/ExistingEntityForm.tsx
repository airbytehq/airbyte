import React, { useMemo } from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import ContentCard from "components/ContentCard";
import { Button, ControlLabels, DropDown } from "components";
import ImageBlock from "components/ImageBlock";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceList } from "../../../../../hooks/services/useSourceHook";
import { useDestinationList } from "../../../../../hooks/services/useDestinationHook";

type IProps = {
  type: "source" | "destination";
  onSubmit: (id: string) => void;
};

const FormContent = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const BottomBlock = styled.div`
  text-align: right;
  margin-top: 34px;
`;

const PaddingBlock = styled.div`
  text-align: center;
  padding: 18px 0 15px;
  font-weight: 500;
  font-size: 15px;
  line-height: 18px;
`;

const existingEntityValidationSchema = yup.object().shape({
  entityId: yup.string().required("form.empty.error"),
});

const ExistingEntityForm: React.FC<IProps> = ({ type, onSubmit }) => {
  const formatMessage = useIntl().formatMessage;
  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();

  const { destinations } = useDestinationList();

  const { destinationDefinitions } = useDestinationDefinitionList();

  const dropDownData = useMemo(() => {
    if (type === "source") {
      return sources.map((item) => {
        const sourceDef = sourceDefinitions.find(
          (sd) => sd.sourceDefinitionId === item.sourceDefinitionId
        );
        return {
          label: item.name,
          value: item.sourceId,
          img: <ImageBlock img={sourceDef?.icon} />,
        };
      });
    } else {
      return destinations.map((item) => {
        const destinationDef = destinationDefinitions.find(
          (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
        );
        return {
          label: item.name,
          value: item.destinationId,
          img: <ImageBlock img={destinationDef?.icon} />,
        };
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  if (!dropDownData.length) {
    return null;
  }

  const initialValues = { entityId: "" };
  return (
    <>
      <ContentCard
        title={<FormattedMessage id={`connectionForm.${type}Existing`} />}
      >
        <Formik
          initialValues={initialValues}
          validationSchema={existingEntityValidationSchema}
          onSubmit={async (values: { entityId: string }, { resetForm }) => {
            onSubmit(values.entityId);
            resetForm({});
          }}
        >
          {({ isSubmitting, setFieldValue }) => (
            <FormContent>
              <Field name="entityId">
                {({ field }: FieldProps<string>) => (
                  <ControlLabels
                    label={formatMessage({
                      id: `connectionForm.${type}Title`,
                    })}
                  >
                    <DropDown
                      {...field}
                      options={dropDownData}
                      onChange={(item: { value: string }) => {
                        setFieldValue(field.name, item.value);
                      }}
                    />
                  </ControlLabels>
                )}
              </Field>
              <BottomBlock>
                <Button disabled={isSubmitting} type="submit">
                  <FormattedMessage id={`connectionForm.${type}Use`} />
                </Button>
              </BottomBlock>
            </FormContent>
          )}
        </Formik>
      </ContentCard>
      <PaddingBlock>
        <FormattedMessage id="onboarding.or" />
      </PaddingBlock>
    </>
  );
};

export default ExistingEntityForm;
