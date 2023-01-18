import { Field } from "formik";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { NormalizationType } from "core/domain/connection";
import { OperationRead } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FormikOnSubmit } from "types/formik";
import { NormalizationField } from "views/Connection/ConnectionForm/components/NormalizationField";
import { getInitialNormalization } from "views/Connection/ConnectionForm/formConfig";
import { FormCard } from "views/Connection/FormCard";

export const NormalizationCard: React.FC<{
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
