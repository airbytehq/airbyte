import { Field, FieldProps, Form, Formik } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { ConnectorIcon } from "components/common/ConnectorIcon";
import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { DropDown } from "components/ui/DropDown";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import styles from "./ExistingEntityForm.module.scss";

interface IProps {
  type: "source" | "destination";
  onSubmit: (id: string) => void;
}

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
  const { formatMessage } = useIntl();
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

  const initialValues = { entityId: "" };
  return (
    <>
      <Card title={<FormattedMessage id={`connectionForm.${type}Existing`} />}>
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
                      isSearchable
                      onChange={(item: { value: string }) => {
                        setFieldValue(field.name, item.value);
                      }}
                    />
                  </ControlLabels>
                )}
              </Field>
              <BottomBlock>
                <Button className={styles.submitButton} disabled={isSubmitting} type="submit">
                  <FormattedMessage id={`connectionForm.${type}Use`} />
                </Button>
              </BottomBlock>
            </FormContent>
          )}
        </Formik>
      </Card>
      <PaddingBlock>
        <FormattedMessage id="onboarding.or" />
      </PaddingBlock>
    </>
  );
};

export default ExistingEntityForm;
