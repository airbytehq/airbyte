import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray } from "formik";

import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import {
  getInitialNormalization,
  getInitialTransformations,
  useDefaultTransformation,
} from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";
import { Connection, Operation } from "core/domain/connection";

type TransformationViewProps = {
  connection: Connection;
};

const Content = styled.div`
  max-width: 1073px;
  margin: 0 auto;
  padding-bottom: 10px;
`;

const CustomTransformationsCard: React.FC<{ operations: Operation[] }> = ({
  operations,
}) => {
  const defaultTransformation = useDefaultTransformation();

  const initialValues = useMemo(
    () => ({
      transformations: getInitialTransformations(operations),
    }),
    [operations]
  );

  return (
    <FormCard
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues,
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

const NormalizationCard: React.FC<{ operations: Operation[] }> = ({
  operations,
}) => {
  const initialValues = useMemo(
    () => ({
      normalization: getInitialNormalization(operations),
    }),
    [operations]
  );
  return (
    <FormCard
      form={{
        initialValues,
        onSubmit: async (value) => console.log(value),
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
    >
      <Field name="normalization" component={NormalizationField} />
    </FormCard>
  );
};

const TransformationView: React.FC<TransformationViewProps> = ({
  connection,
}) => {
  return (
    <Content>
      <NormalizationCard operations={connection.operations} />
      <CustomTransformationsCard operations={connection.operations} />
    </Content>
  );
};

export default TransformationView;
