import { Field, FieldArray } from "formik";
import React from "react";
import { useIntl } from "react-intl";

import { Card, H5 } from "components";

import { useConnectionFormService } from "hooks/services/Connection/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { StyledSection } from "../ConnectionForm";
import { NormalizationField } from "./NormalizationField";
import { TransformationField } from "./TransformationField";

interface OperationsSectionProps {
  onStartEditTransformation?: () => void;
  onEndEditTransformation?: () => void;
}

export const OperationsSection: React.FC<OperationsSectionProps> = ({
  onStartEditTransformation,
  onEndEditTransformation,
}) => {
  const { formatMessage } = useIntl();

  const {
    destDefinition: { supportsNormalization, supportsDbt },
  } = useConnectionFormService();

  const supportsTransformations = useFeature(FeatureItem.AllowCustomDBT) && supportsDbt;

  if (!supportsNormalization && !supportsTransformations) {
    return null;
  }

  return (
    <Card>
      <StyledSection>
        {supportsNormalization || supportsTransformations ? (
          <H5 bold>
            {[
              supportsNormalization && formatMessage({ id: "connectionForm.normalization.title" }),
              supportsTransformations && formatMessage({ id: "connectionForm.transformation.title" }),
            ]
              .filter(Boolean)
              .join(" & ")}
          </H5>
        ) : null}
        {supportsNormalization && <Field name="normalization" component={NormalizationField} />}
        {supportsTransformations && (
          <FieldArray name="transformations">
            {(formProps) => (
              <TransformationField
                onStartEdit={onStartEditTransformation}
                onEndEdit={onEndEditTransformation}
                {...formProps}
              />
            )}
          </FieldArray>
        )}
      </StyledSection>
    </Card>
  );
};
