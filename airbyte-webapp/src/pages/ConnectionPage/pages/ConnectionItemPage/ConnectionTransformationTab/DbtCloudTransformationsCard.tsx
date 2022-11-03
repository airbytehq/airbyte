import { faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, Form, Formik, FieldArray, FieldProps, FormikHelpers } from "formik";
import { Link } from "react-router-dom";
import { array, object, number } from "yup";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Input } from "components/ui/Input";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { DbtCloudJob, useDbtIntegration } from "packages/cloud/services/dbtCloud";
import { RoutePaths } from "pages/routePaths";

import styles from "./DbtCloudTransformationsCard.module.scss";

interface DbtJobListValues {
  jobs: DbtCloudJob[];
}

const dbtCloudJobListSchema = object({
  jobs: array().of(
    object({
      account: number().required().positive().integer(),
      job: number().required().positive().integer(),
    })
  ),
});

export const DbtCloudTransformationsCard = ({ connection }: { connection: WebBackendConnectionRead }) => {
  // Possible render paths:
  // 1) IF the workspace has no dbt cloud account linked
  //    THEN show "go to your settings to connect your dbt Cloud Account" text
  //    and the "Don't have a dbt account?" hero/media element
  // 2) IF the workspace has a dbt cloud account linked...
  //   2.1) AND the connection has no saved dbt jobs (cf: operations)
  //        THEN show empty jobs list and the "+ Add transformation" button
  //   2.2) AND the connection has saved dbt jobs
  //        THEN show the jobs list and the "+ Add transformation" button

  const { hasDbtIntegration, saveJobs, dbtCloudJobs } = useDbtIntegration(connection);
  const onSubmit = (values: DbtJobListValues, { resetForm }: FormikHelpers<DbtJobListValues>) => {
    saveJobs(values.jobs).then(() => resetForm({ values }));
  };

  return (
    <Formik // TODO extract to parent component, see if that helps with input focus issues
      onSubmit={onSubmit}
      initialValues={{ jobs: dbtCloudJobs }}
      validationSchema={dbtCloudJobListSchema}
      render={({ values, isValid, dirty }) => {
        return (
          <Form className={styles.jobListForm}>
            <FormChangeTracker changed={dirty} />
            <FieldArray
              name="jobs"
              render={({ remove, push }) => {
                return (
                  <Card
                    title={
                      <span className={styles.jobListTitle}>
                        Transformations
                        {hasDbtIntegration && (
                          <Button
                            variant="secondary"
                            onClick={() => push({ account: "", job: "" })}
                            icon={<FontAwesomeIcon icon={faPlus} />}
                          >
                            Add transformation
                          </Button>
                        )}
                      </span>
                    }
                  >
                    {hasDbtIntegration ? (
                      <DbtJobsList jobs={values.jobs} remove={remove} isValid={isValid} dirty={dirty} />
                    ) : (
                      <NoDbtIntegration className={styles.jobListContainer} />
                    )}
                  </Card>
                );
              }}
            />
          </Form>
        );
      }}
    />
  );
};

const DbtJobsList = ({
  jobs,
  remove,
  isValid,
  dirty,
}: {
  jobs: DbtCloudJob[];
  remove: (i: number) => void;
  isValid: boolean;
  dirty: boolean;
}) => (
  <div className={classNames(styles.jobListContainer, styles.emptyListContent)}>
    <p className={styles.contextExplanation}>After an Airbyte sync job has completed, the following jobs will run</p>
    {jobs.length ? (
      jobs.map((_j, i) => <JobsListItem key={i} jobIndex={i} removeJob={() => remove(i)} />)
    ) : (
      <>
        <img src="/images/octavia/worker.png" alt="An octopus wearing a hard hat, tools at the ready" />
        No transformations
      </>
    )}
    <div className={styles.jobListButtonGroup}>
      <Button className={styles.jobListButton} type="reset" variant="secondary">
        Cancel
      </Button>
      <Button className={styles.jobListButton} type="submit" variant="primary" disabled={!dirty || !isValid}>
        Save changes
      </Button>
    </div>
  </div>
);

// TODO give feedback on validation errors (red outline and validation message)
const JobsListItem = ({ jobIndex, removeJob }: { jobIndex: number; removeJob: () => void }) => {
  return (
    <Card className={styles.jobListItem}>
      <div className={styles.jobListItemIntegrationName}>
        <img src="/images/external/dbt-bit_tm.png" alt="dbt logo" />
        dbt Cloud transform
      </div>
      <div className={styles.jobListItemInputGroup}>
        <div className={styles.jobListItemInput}>
          <Field name={`jobs.${jobIndex}.account`}>
            {({ field }: FieldProps<string>) => (
              <>
                <label htmlFor={`jobs.${jobIndex}.account`} className={styles.jobListItemInputLabel}>
                  Account ID
                </label>
                <Input {...field} type="text" />
              </>
            )}
          </Field>
        </div>
        <div className={styles.jobListItemInput}>
          <Field name={`jobs.${jobIndex}.job`}>
            {({ field }: FieldProps<string>) => (
              <>
                <label htmlFor={`jobs.${jobIndex}.job`} className={styles.jobListItemInputLabel}>
                  Job ID
                </label>
                <Input {...field} type="text" />
              </>
            )}
          </Field>
        </div>
        <button type="button" className={styles.jobListItemDelete} onClick={removeJob}>
          <FontAwesomeIcon icon={faXmark} />
        </button>
      </div>
    </Card>
  );
};

const NoDbtIntegration = ({ className }: { className: string }) => {
  const { workspaceId } = useCurrentWorkspace();
  const dbtSettingsPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Settings}/dbt-cloud`;
  return (
    <div className={classNames(className, styles.emptyListContent)}>
      <p className={styles.contextExplanation}>After an Airbyte sync job has completed, the following jobs will run</p>
      <p className={styles.contextExplanation}>
        Go to your <Link to={dbtSettingsPath}>settings</Link> to connect your dbt Cloud account
      </p>
      <DbtCloudSignupBanner />
    </div>
  );
};

const DbtCloudSignupBanner = () => <div />;
