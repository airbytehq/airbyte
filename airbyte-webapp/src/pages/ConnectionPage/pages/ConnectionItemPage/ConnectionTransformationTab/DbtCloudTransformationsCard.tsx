import { faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, Form, Formik, FieldArray, FieldProps, FormikHelpers } from "formik";
import { ReactNode } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Link } from "react-router-dom";
import * as yup from "yup";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { DbtCloudJob, useDbtIntegration } from "packages/cloud/services/dbtCloud";
import { RoutePaths } from "pages/routePaths";

import dbtLogo from "./dbt-bit_tm.svg";
import styles from "./DbtCloudTransformationsCard.module.scss";
import octaviaWorker from "./octavia-worker.png";

interface DbtJobListValues {
  jobs: DbtCloudJob[];
}

const dbtCloudJobListSchema = yup.object({
  jobs: yup.array().of(
    yup.object({
      account: yup.number().required().positive().integer(),
      job: yup.number().required().positive().integer(),
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
    <Formik
      onSubmit={onSubmit}
      initialValues={{ jobs: dbtCloudJobs }}
      validationSchema={dbtCloudJobListSchema}
      render={({ values, isValid, dirty }) => {
        return hasDbtIntegration ? (
          <Form className={styles.jobListForm}>
            <FormChangeTracker changed={dirty} />
            <FieldArray
              name="jobs"
              render={({ remove, push }) => {
                return (
                  <Card
                    title={
                      <span className={styles.jobListTitle}>
                        <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
                        <Button
                          variant="secondary"
                          onClick={() => push({ account: "", job: "" })}
                          icon={<FontAwesomeIcon icon={faPlus} />}
                        >
                          <FormattedMessage id="connection.dbtCloudJobs.addJob" />
                        </Button>
                      </span>
                    }
                  >
                    <DbtJobsList jobs={values.jobs} remove={remove} isValid={isValid} dirty={dirty} />
                  </Card>
                );
              }}
            />
          </Form>
        ) : (
          <Card
            title={
              <span className={styles.jobListTitle}>
                <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
              </span>
            }
          >
            <NoDbtIntegration />
          </Card>
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
  <div className={classNames(styles.jobListContainer)}>
    {jobs.length ? (
      <>
        <Text className={styles.contextExplanation}>
          <FormattedMessage id="connection.dbtCloudJobs.explanation" />
        </Text>
        {jobs.map((_, i) => (
          <JobsListItem key={i} jobIndex={i} removeJob={() => remove(i)} />
        ))}
      </>
    ) : (
      <>
        <img src={octaviaWorker} alt="" className={styles.emptyListImage} />
        <FormattedMessage id="connection.dbtCloudJobs.noJobs" />
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
  const { formatMessage } = useIntl();
  return (
    <Card className={styles.jobListItem}>
      <div className={styles.jobListItemIntegrationName}>
        <img src={dbtLogo} alt="" className={styles.dbtLogo} />
        <FormattedMessage id="connection.dbtCloudJobs.job.title" />
      </div>
      <div className={styles.jobListItemInputGroup}>
        <div className={styles.jobListItemInput}>
          <Field name={`jobs.${jobIndex}.account`}>
            {({ field }: FieldProps<string>) => (
              <>
                <label htmlFor={`jobs.${jobIndex}.account`} className={styles.jobListItemInputLabel}>
                  <FormattedMessage id="connection.dbtCloudJobs.job.accountId" />
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
                  <FormattedMessage id="connection.dbtCloudJobs.job.jobId" />
                </label>
                <Input {...field} type="text" />
              </>
            )}
          </Field>
        </div>
        <Button
          variant="clear"
          size="lg"
          className={styles.jobListItemDelete}
          onClick={removeJob}
          aria-label={formatMessage({ id: "connection.dbtCloudJobs.job.deleteButton" })}
        >
          <FontAwesomeIcon icon={faXmark} />
        </Button>
      </div>
    </Card>
  );
};

const NoDbtIntegration = () => {
  const { workspaceId } = useCurrentWorkspace();
  const dbtSettingsPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Settings}/dbt-cloud`;
  return (
    <div className={classNames(styles.jobListContainer)}>
      <Text className={styles.contextExplanation}>
        <FormattedMessage
          id="connection.dbtCloudJobs.noIntegration"
          values={{
            settingsLink: (linkText: ReactNode) => <Link to={dbtSettingsPath}>{linkText}</Link>,
          }}
        />
      </Text>
    </div>
  );
};
