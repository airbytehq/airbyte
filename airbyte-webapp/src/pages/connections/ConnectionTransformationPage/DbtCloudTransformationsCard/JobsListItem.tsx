import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Text } from "components/ui/Text";

import { DbtCloudJob } from "packages/cloud/services/dbtCloud";

import dbtLogo from "./dbt-bit_tm.svg";
import styles from "./JobsListItem.module.scss";

interface JobsListItemProps {
  job: DbtCloudJob;
  removeJob: () => void;
  isLoading: boolean;
}
export const JobsListItem = ({ job, removeJob, isLoading }: JobsListItemProps) => {
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
