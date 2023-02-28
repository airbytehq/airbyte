import { Field, FieldArray } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";

import { H3 } from "components";

import { FeatureItem, useFeature } from "hooks/services/Feature";

import { DestinationDefinitionSpecificationRead } from "../../../../core/request/AirbyteClient";
import { useDefaultTransformation } from "../formConfig";
import { NormalizationField } from "./NormalizationField";
import { TransformationField } from "./TransformationField";

interface OperationsSectionProps {
  destDefinition: DestinationDefinitionSpecificationRead;
  onStartEditTransformation?: () => void;
  onEndEditTransformation?: () => void;
  wrapper: React.ComponentType;
}

const SectionTitle = styled(H3)`
  margin-bottom: 30px;
`;

export const OperationsSection: React.FC<OperationsSectionProps> = ({
  destDefinition,
  onStartEditTransformation,
  onEndEditTransformation,
  wrapper: Wrapper,
}) => {
  const { formatMessage } = useIntl();

  const { supportsNormalization } = destDefinition;
  const supportsTransformations = useFeature(FeatureItem.AllowCustomDBT) && destDefinition.supportsDbt;

  const defaultTransformation = useDefaultTransformation();

  if (!supportsNormalization && !supportsTransformations) {
    return null;
  }

  return (
    <Wrapper>
      {supportsNormalization || supportsTransformations ? (
        <SectionTitle bold>
          {[
            supportsNormalization && formatMessage({ id: "connectionForm.normalization.title" }),
            supportsTransformations && formatMessage({ id: "connectionForm.transformation.title" }),
          ]
            .filter(Boolean)
            .join(" & ")}
        </SectionTitle>
      ) : null}
      {supportsNormalization && <Field name="normalization" component={NormalizationField} />}
      {supportsTransformations && (
        <FieldArray name="transformations">
          {(formProps) => (
            <TransformationField
              defaultTransformation={defaultTransformation}
              onStartEdit={onStartEditTransformation}
              onEndEdit={onEndEditTransformation}
              {...formProps}
            />
          )}
        </FieldArray>
      )}
    </Wrapper>
  );
};
