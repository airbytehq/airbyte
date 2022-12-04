import { Field, FieldArray } from "formik";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useToggle } from "react-use";

import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import { NormalizationType } from "core/domain/connection";
import { OperationCreate, OperationRead, OperatorType } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { FormikOnSubmit } from "types/formik";
import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { TransformationField } from "views/Connection/ConnectionForm/components/TransformationField";
import {
  getInitialNormalization,
  getInitialTransformations,
  mapFormPropsToOperation,
} from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";

import styles from "./ConnectionTransformationTab.module.scss";
import { DbtCloudTransformationsCard } from "./ConnectionTransformationTab/DbtCloudTransformationsCard";

const CustomTransformationsCard: React.FC<{
  operations?: OperationCreate[];
  onSubmit: FormikOnSubmit<{ transformations?: OperationRead[] }>;
}> = ({ operations, onSubmit }) => {
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { mode } = useConnectionFormService();
  const initialValues = useMemo(
    () => ({
      transformations: getInitialTransformations(operations || []),
    }),
    [operations]
  );

  return (
    <FormCard<{ transformations?: OperationRead[] }>
      title={<FormattedMessage id="connection.customTransformations" />}
      collapsible
      bottomSeparator
      form={{
        initialValues,
        enableReinitialize: true,
        onSubmit,
      }}
      submitDisabled={editingTransformation}
    >
      <FieldArray name="transformations">
        {(formProps) => (
          <TransformationField
            {...formProps}
            mode={mode}
            onStartEdit={toggleEditingTransformation}
            onEndEdit={toggleEditingTransformation}
          />
        )}
      </FieldArray>
    </FormCard>
  );
};

const NormalizationCard: React.FC<{
  operations?: OperationRead[];
  onSubmit: FormikOnSubmit<{ normalization?: NormalizationType }>;
}> = ({ operations, onSubmit }) => {
  const { mode } = useConnectionFormService();
  const initialValues = useMemo(
    () => ({
      normalization: getInitialNormalization(operations, true),
    }),
    [operations]
  );

  return (
    <FormCard<{ normalization?: NormalizationType }>
      form={{
        initialValues,
        onSubmit,
      }}
      title={<FormattedMessage id="connection.normalization" />}
      collapsible
    >
      <Field name="normalization" component={NormalizationField} mode={mode} />
    </FormCard>
  );
};

export const ConnectionTransformationTab: React.FC = () => {
  const { connection, updateConnection } = useConnectionEditService();
  const { mode } = useConnectionFormService();
  const definition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const workspace = useCurrentWorkspace();

  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_TRANSFORMATION);
  const { supportsNormalization } = definition;
  const supportsDbt = useFeature(FeatureItem.AllowCustomDBT) && definition.supportsDbt;
  const supportsCloudDbtIntegration = useFeature(FeatureItem.AllowDBTCloudIntegration) && definition.supportsDbt;
  const noSupportedTransformations = !supportsNormalization && !supportsDbt && !supportsCloudDbtIntegration;

  const onSubmit: FormikOnSubmit<{ transformations?: OperationRead[]; normalization?: NormalizationType }> = async (
    values,
    { resetForm }
  ) => {
    const newOp = mapFormPropsToOperation(values, connection.operations, workspace.workspaceId);

    const operations = values.transformations
      ? (connection.operations as OperationCreate[]) // There's an issue meshing the OperationRead here with OperationCreate that we want, in the types
          ?.filter((op) => op.operatorConfiguration.operatorType === OperatorType.normalization)
          .concat(newOp)
      : newOp.concat(
          (connection.operations ?? [])?.filter((op) => op.operatorConfiguration.operatorType === OperatorType.dbt)
        );

    await updateConnection({ connectionId: connection.connectionId, operations });

    const nextFormValues: typeof values = {};
    if (values.transformations) {
      nextFormValues.transformations = getInitialTransformations(operations);
    }
    nextFormValues.normalization = getInitialNormalization(operations, true);

    resetForm({ values: nextFormValues });
  };

  return (
    <div className={styles.content}>
      <fieldset
        disabled={mode === "readonly"}
        style={{ border: "0", pointerEvents: `${mode === "readonly" ? "none" : "auto"}` }}
      >
        {supportsNormalization && <NormalizationCard operations={connection.operations} onSubmit={onSubmit} />}
        {supportsDbt && <CustomTransformationsCard operations={connection.operations} onSubmit={onSubmit} />}
        {supportsCloudDbtIntegration && <DbtCloudTransformationsCard connection={connection} />}
        {noSupportedTransformations && (
          <Card className={styles.customCard}>
            <Text size="lg" centered>
              <FormattedMessage id="connectionForm.operations.notSupported" />
            </Text>
          </Card>
        )}
      </fieldset>
    </div>
  );
};
