import { Field, FieldArray } from "formik";
import React from "react";
import { useIntl } from "react-intl";

import { Card } from "components/ui/Card";
import { Heading } from "components/ui/Heading";

import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import { NormalizationField } from "./NormalizationField";
import { Section } from "./Section";
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
      <Section>
        {supportsNormalization || supportsTransformations ? (
          <Heading as="h5">
            {[
              supportsNormalization && formatMessage({ id: "connectionForm.normalization.title" }),
              supportsTransformations && formatMessage({ id: "connectionForm.transformation.title" }),
            ]
              .filter(Boolean)
              .join(" & ")}
          </Heading>
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
      </Section>
    </Card>
  );
};
