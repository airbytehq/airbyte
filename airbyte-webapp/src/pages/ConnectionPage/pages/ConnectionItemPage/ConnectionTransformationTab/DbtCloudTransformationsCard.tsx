import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import styles from "./DbtCloudTransformationsCard.module.scss";

// This won't be used by the first prototype, but it is the UI specced in
// follow-up designs which can support multiple integrations; it's also a small,
// self-contained set of components and scss which will only trivially affect
// bundle size.
// eslint-disable-next-line: @typescript-eslint/no-usused-vars @typescript-eslint/ban-ts-comment
// @ts-ignore: no unused locals
const EmptyTransformationsList = ({ className }: { className: string }) => (
  <div className={classNames(className, styles.emptyListContent)}>
    <div className={styles.contextExplanation}>
      After an Airbyte sync job has completed, the following jobs will run.
    </div>
    <img src="/images/octavia/worker.png" alt="An octopus wearing a hard hat, tools at the ready" />
    No transformations
  </div>
);

export const DbtCloudTransformationsCard = () => {
  // Possible render paths:
  // 1) IF the workspace has no dbt cloud account linked
  //    THEN show "go to your settings to connect your dbt Cloud Account" text
  //    and the "Don't have a dbt account?" hero/media element
  // 2) IF the workspace has a dbt cloud account linked...
  //   2.1) AND the connection has no saved dbt jobs (cf: operations)
  //        THEN show empty jobs list and the "+ Add transformation" button
  //   2.2) AND the connection has saved dbt jobs
  //        THEN show the "no jobs" card body and the "+ Add transformation" button
  const transformations = [];
  /* const transformations = [1, 2, 3]; */

  const TransformationList = ({ className }: { className: string }) =>
    transformations.length ? (
      <div className={className}>this is a list</div>
    ) : (
      <EmptyTransformationsList className={className} />
    );

  return (
    <Card
      title={
        <span className={styles.cloudTransformationsListTitle}>
          Transformations
          <Button variant="secondary" icon={<FontAwesomeIcon icon={faPlus} />}>
            Add transformation
          </Button>
        </span>
      }
    >
      <TransformationList className={styles.cloudTransformationsListContainer} />
    </Card>
  );
};
