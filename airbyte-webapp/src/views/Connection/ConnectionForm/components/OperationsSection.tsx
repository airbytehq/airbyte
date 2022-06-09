import { Field, FieldArray } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";

import { FeatureItem, useFeatureService } from "hooks/services/Feature";

import { DestinationDefinitionSpecificationRead } from "../../../../core/request/AirbyteClient";
import { useDefaultTransformation } from "../formConfig";
import { NormalizationField } from "./NormalizationField";
import { TransformationField } from "./TransformationField";

const SectionTitle = styled.div`
  font-weight: bold;
  font-size: 14px;
  line-height: 17px;
`;

export const OperationsSection: React.FC<{
  destDefinition: DestinationDefinitionSpecificationRead;
}> = ({ destDefinition }) => {
  const formatMessage = useIntl().formatMessage;
  const { hasFeature } = useFeatureService();

  const supportsNormalization = destDefinition.supportsNormalization;
  const supportsTransformations = destDefinition.supportsDbt && hasFeature(FeatureItem.AllowCustomDBT);

  const defaultTransformation = useDefaultTransformation();

  return (
    <>
      {supportsNormalization || supportsTransformations ? (
        <SectionTitle>
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
          {(formProps) => <TransformationField defaultTransformation={defaultTransformation} {...formProps} />}
        </FieldArray>
      )}
    </>
  );
};
