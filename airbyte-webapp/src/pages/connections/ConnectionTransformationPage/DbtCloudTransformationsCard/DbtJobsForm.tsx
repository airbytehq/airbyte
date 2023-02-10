import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Form, Formik, FieldArray, FormikHelpers } from "formik";
import { FormattedMessage } from "react-intl";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { DropdownMenu } from "components/ui/DropdownMenu";

import { DbtCloudJobInfo } from "packages/cloud/lib/domain/dbtCloud";
import { DbtCloudJob, isSameJob } from "packages/cloud/services/dbtCloud";

import styles from "./DbtJobsForm.module.scss";
import { JobsList } from "./JobsList";

interface DbtJobListValues {
  jobs: DbtCloudJob[];
}

interface DbtJobsFormProps {
  saveJobs: (jobs: DbtCloudJob[]) => Promise<unknown>;
  isSaving: boolean;
  dbtCloudJobs: DbtCloudJob[];
  availableDbtCloudJobs: DbtCloudJobInfo[];
}

export const DbtJobsForm: React.FC<DbtJobsFormProps> = ({
  saveJobs,
  isSaving,
  dbtCloudJobs,
  availableDbtCloudJobs,
}) => {
  const onSubmit = (values: DbtJobListValues, { resetForm }: FormikHelpers<DbtJobListValues>) => {
    saveJobs(values.jobs).then(() => resetForm({ values }));
  };

  // because we don't store names for saved jobs, just the account and job IDs needed for
  // webhook operation, we have to find the display names for saved jobs by comparing IDs
  // with the list of available jobs as provided by dbt Cloud.
  const jobs = dbtCloudJobs.map((savedJob) => {
    const { jobName } = availableDbtCloudJobs.find((remoteJob) => isSameJob(remoteJob, savedJob)) || {};
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
                      <span className={styles.cardTitle}>
                        <FormattedMessage id="connection.dbtCloudJobs.cardTitle" />
                        <DropdownMenu
                          options={availableDbtCloudJobs
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
                    <JobsList jobs={values.jobs} remove={remove} dirty={dirty} isLoading={isSaving} />
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
