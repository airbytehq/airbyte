import classNames from "classnames";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { DbtCloudJob } from "packages/cloud/services/dbtCloud";

import styles from "./JobsList.module.scss";
import { JobsListItem } from "./JobsListItem";
import octaviaWorker from "./octavia-worker.png";

interface JobsListProps {
  jobs: DbtCloudJob[];
  remove: (i: number) => void;
  dirty: boolean;
  isLoading: boolean;
}

export const JobsList = ({ jobs, remove, dirty, isLoading }: JobsListProps) => {
  const { formatMessage } = useIntl();

  return (
    <div className={classNames(styles.cardBodyContainer)}>
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
