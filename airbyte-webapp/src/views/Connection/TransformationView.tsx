import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray } from "formik";
import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import { useDefaultTransformation } from "views/Connection/ConnectionForm/formConfig";

import { FormCard } from "./FormCard";

type TransformationViewProps = {};

const Content = styled.div`
  max-width: 1073px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const CustomTransformationsCard: React.FC = () => {
  const defaultTransformation = useDefaultTransformation();

  return (
    <FormCard
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues: { transformations: [] },
        onSubmit: async (value) => console.log(value),
      }}
    >
      <FieldArray name="transformations">
        {(formProps) => (
          <TransformationField
            defaultTransformation={defaultTransformation}
            {...formProps}
          />
        )}
      </FieldArray>
    </FormCard>
  );
};

const NormalizationCard: React.FC = () => {
  return (
    <FormCard
      form={{
        initialValues: {
          normalization: "",
        },
        onSubmit: async (value) => console.log(value),
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
    >
      <Field name="normalization" component={NormalizationField} />
    </FormCard>
  );
};

const TransformationView: React.FC<TransformationViewProps> = () => {
  return (
    <Content>
      <NormalizationCard />
      <CustomTransformationsCard />
    </Content>
  );
};

export default TransformationView;
