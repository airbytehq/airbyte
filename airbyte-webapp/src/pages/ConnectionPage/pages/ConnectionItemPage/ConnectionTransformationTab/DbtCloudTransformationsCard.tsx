import { faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Form, Formik, FieldArray, FormikHelpers } from "formik";
import { ReactNode } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Link } from "react-router-dom";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { DropdownMenu } from "components/ui/DropdownMenu";
import { Text } from "components/ui/Text";

import { WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { DbtCloudJob, isSameJob, useDbtIntegration, useAvailableDbtJobs } from "packages/cloud/services/dbtCloud";
import { RoutePaths } from "pages/routePaths";

import dbtLogo from "./dbt-bit_tm.svg";
import styles from "./DbtCloudTransformationsCard.module.scss";
import octaviaWorker from "./octavia-worker.png";

interface DbtJobListValues {
  jobs: DbtCloudJob[];
}

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

  const { hasDbtIntegration, isSaving, saveJobs, dbtCloudJobs } = useDbtIntegration(connection);

  return hasDbtIntegration ? (
    <DbtJobsForm saveJobs={saveJobs} isSaving={isSaving} dbtCloudJobs={dbtCloudJobs} />
  ) : (
    <NoDbtIntegration />
  );
};

const NoDbtIntegration = () => {
  const { workspaceId } = useCurrentWorkspace();
  const dbtSettingsPath = `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Settings}/dbt-cloud`;
  return (
    <Card
      title={
        <span className={styles.jobListTitle}>
          <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
        </span>
      }
    >
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
    </Card>
  );
};

interface DbtJobsFormProps {
  saveJobs: (jobs: DbtCloudJob[]) => Promise<unknown>;
  isSaving: boolean;
  dbtCloudJobs: DbtCloudJob[];
}
const DbtJobsForm: React.FC<DbtJobsFormProps> = ({ saveJobs, isSaving, dbtCloudJobs }) => {
  const onSubmit = (values: DbtJobListValues, { resetForm }: FormikHelpers<DbtJobListValues>) => {
    saveJobs(values.jobs).then(() => resetForm({ values }));
  };

  const availableDbtJobs = useAvailableDbtJobs();
  // because we don't store names for saved jobs, just the account and job IDs needed for
  // webhook operation, we have to find the display names for saved jobs by comparing IDs
  // with the list of available jobs as provided by dbt Cloud.
  const jobs = dbtCloudJobs.map((savedJob) => {
    const { jobName } = availableDbtJobs.find((remoteJob) => isSameJob(remoteJob, savedJob)) || {};
    const { accountId, jobId } = savedJob;

    return { accountId, jobId, jobName };
  });

  return (
    <Formik
      onSubmit={onSubmit}
      initialValues={{ jobs }}
      render={({ values, dirty }) => {
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
                        <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
                        <DropdownMenu
                          options={availableDbtJobs
                            .filter((remoteJob) => !values.jobs.some((savedJob) => isSameJob(remoteJob, savedJob)))
                            .map((job) => ({ displayName: job.jobName, value: job }))}
                          onChange={(selection) => {
                            push(selection.value);
                          }}
                        >
                          {() => (
                            <Button variant="secondary" icon={<FontAwesomeIcon icon={faPlus} />}>
                              <FormattedMessage id="connection.dbtCloudJobs.addJob" />
                            </Button>
                          )}
                        </DropdownMenu>
                      </span>
                    }
                  >
                    <DbtJobsList jobs={values.jobs} remove={remove} dirty={dirty} isLoading={isSaving} />
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

interface DbtJobsListProps {
  jobs: DbtCloudJob[];
  remove: (i: number) => void;
  dirty: boolean;
  isLoading: boolean;
}

const DbtJobsList = ({ jobs, remove, dirty, isLoading }: DbtJobsListProps) => {
  const { formatMessage } = useIntl();

  return (
    <div className={classNames(styles.jobListContainer)}>
      {jobs.length ? (
        <>
          <Text className={styles.contextExplanation}>
            <FormattedMessage id="connection.dbtCloudJobs.explanation" />
          </Text>
          {jobs.map((job, i) => (
            <JobsListItem key={i} job={job} removeJob={() => remove(i)} isLoading={isLoading} />
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
          {formatMessage({ id: "form.cancel" })}
        </Button>
        <Button
          className={styles.jobListButton}
          type="submit"
          variant="primary"
          disabled={!dirty}
          isLoading={isLoading}
        >
          {formatMessage({ id: "form.saveChanges" })}
        </Button>
      </div>
    </div>
  );
};

interface JobsListItemProps {
  job: DbtCloudJob;
  removeJob: () => void;
  isLoading: boolean;
}
const JobsListItem = ({ job, removeJob, isLoading }: JobsListItemProps) => {
  const { formatMessage } = useIntl();
  // TODO if `job.jobName` is undefined, that means we failed to match any of the
  // dbt-Cloud-supplied jobs with the saved job. This means one of two things has
  // happened:
  // 1) the user deleted the job in dbt Cloud, and we should make them delete it from
  //    their webhook operations. If we have a nonempty list of other dbt Cloud jobs,
  //    it's definitely this.
  // 2) the API call to fetch the names failed somehow (possibly with a 200 status, if there's a bug)
  const title = <Text>{job.jobName || formatMessage({ id: "connection.dbtCloudJobs.job.title" })}</Text>;

  return (
    <Card className={styles.jobListItem}>
      <div className={styles.jobListItemIntegrationName}>
        <img src={dbtLogo} alt="" className={styles.dbtLogo} />
        {title}
      </div>
      <div className={styles.jobListItemIdFieldGroup}>
        <div className={styles.jobListItemIdField}>
          <Text size="sm">
            {formatMessage({ id: "connection.dbtCloudJobs.job.accountId" })}: {job.accountId}
          </Text>
        </div>
        <div className={styles.jobListItemIdField}>
          <Text size="sm">
            {formatMessage({ id: "connection.dbtCloudJobs.job.jobId" })}: {job.jobId}
          </Text>
        </div>
        <Button
          variant="clear"
          size="lg"
          className={styles.jobListItemDelete}
          onClick={removeJob}
          disabled={isLoading}
          aria-label={formatMessage({ id: "connection.dbtCloudJobs.job.deleteButton" })}
        >
          <FontAwesomeIcon icon={faXmark} height="21" width="21" />
        </Button>
      </div>
    </Card>
  );
};
