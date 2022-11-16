import type { FormikErrors } from "formik/dist/types";

import { getIn, useFormik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { ControlLabels } from "components/LabeledControl";
import { Button } from "components/ui/Button";
import { DropDown } from "components/ui/DropDown";
import { Input } from "components/ui/Input";
import { ModalBody, ModalFooter } from "components/ui/Modal";

import { OperationService } from "core/domain/connection";
import { OperationCreate, OperationRead } from "core/request/AirbyteClient";
import { useGetService } from "core/servicesProvider";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { links } from "utils/links";
import { equal } from "utils/objects";

import styles from "./TransformationForm.module.scss";
import { validationSchema } from "./utils";

interface TransformationProps {
  transformation: OperationCreate;
  onCancel: () => void;
  onDone: (tr: OperationCreate) => void;
  isNewTransformation?: boolean;
}

function prepareLabelFields(
  errors: FormikErrors<OperationRead>,
  name: string
): { error?: boolean; message?: React.ReactNode } {
  const error = getIn(errors, name);

  const fields: { error?: boolean; message?: React.ReactNode } = {};

  if (error) {
    fields.error = true;
    fields.message = <FormattedMessage id={error} />;
  }

  return fields;
}

// enum with only one value for the moment
const TransformationTypes = [{ value: "custom", label: "Custom DBT" }];

const TransformationForm: React.FC<TransformationProps> = ({
  transformation,
  onCancel,
  onDone,
  isNewTransformation,
}) => {
  const { formatMessage } = useIntl();
  const operationService = useGetService<OperationService>("OperationService");
  const { clearFormChange } = useFormChangeTrackerService();
  const formId = useUniqueFormId();

  const formik = useFormik({
    initialValues: transformation,
    validationSchema,
    onSubmit: async (values) => {
      await operationService.check(values);
      clearFormChange(formId);
      onDone(values);
    },
  });

  const onFormCancel: React.MouseEventHandler<HTMLButtonElement> = () => {
    clearFormChange(formId);
    onCancel?.();
  };

  return (
    <>
      <FormChangeTracker changed={isNewTransformation || formik.dirty} formId={formId} />
      <ModalBody maxHeight={400}>
        <div className={styles.content}>
          <div className={styles.column}>
            <ControlLabels
              className={styles.label}
              {...prepareLabelFields(formik.errors, "name")}
              label={<FormattedMessage id="form.transformationName" />}
            >
              <Input {...formik.getFieldProps("name")} />
            </ControlLabels>

            <ControlLabels
              className={styles.label}
              {...prepareLabelFields(formik.errors, "operatorConfiguration.dbt.dockerImage")}
              label={<FormattedMessage id="form.dockerUrl" />}
            >
              <Input {...formik.getFieldProps("operatorConfiguration.dbt.dockerImage")} />
            </ControlLabels>
            <ControlLabels
              className={styles.label}
              {...prepareLabelFields(formik.errors, "operatorConfiguration.dbt.gitRepoUrl")}
              label={<FormattedMessage id="form.repositoryUrl" />}
            >
              <Input
                {...formik.getFieldProps("operatorConfiguration.dbt.gitRepoUrl")}
                placeholder={formatMessage(
                  {
                    id: "form.repositoryUrl.placeholder",
                  },
                  { angle: (node: React.ReactNode) => `<${node}>` }
                )}
              />
            </ControlLabels>
          </div>

          <div className={styles.column}>
            <ControlLabels className={styles.label} label={<FormattedMessage id="form.transformationType" />}>
              <DropDown
                options={TransformationTypes}
                value="custom"
                placeholder={formatMessage({ id: "form.selectType" })}
              />
            </ControlLabels>
            <ControlLabels
              className={styles.label}
              {...prepareLabelFields(formik.errors, "operatorConfiguration.dbt.dbtArguments")}
              label={
                <FormattedMessage
                  id="form.entrypoint.linked"
                  values={{
                    a: (node: React.ReactNode) => (
                      <a href={links.dbtCommandsReference} target="_blank" rel="noreferrer">
                        {node}
                      </a>
                    ),
                  }}
                />
              }
            >
              <Input {...formik.getFieldProps("operatorConfiguration.dbt.dbtArguments")} />
            </ControlLabels>
            <ControlLabels className={styles.label} label={<FormattedMessage id="form.gitBranch" />}>
              <Input {...formik.getFieldProps("operatorConfiguration.dbt.gitRepoBranch")} />
            </ControlLabels>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <Button onClick={onFormCancel} type="button" variant="secondary">
          <FormattedMessage id="form.cancel" />
        </Button>
        <Button
          onClick={() => formik.handleSubmit()}
          type="button"
          data-testid="done-button"
          isLoading={formik.isSubmitting}
          disabled={!formik.isValid || !formik.dirty || equal(transformation, formik.values)}
        >
          <FormattedMessage id="form.saveTransformation" />
        </Button>
      </ModalFooter>
    </>
  );
};

export default TransformationForm;
