import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import styles from "./DbtCloudTransformationsCard.module.scss";

export const DbtCloudTransformationsCard = () => {
  // TODO fetch list of transformations for real
  const transformations = [];
  /* const transformations = [1, 2, 3]; */

  const TransformationList = ({ className }: { className: string }) =>
    transformations.length ? (
      <div className={className}>this is a list</div>
    ) : (
      <div className={classNames(className, styles.emptyListContent)}>
        <div className={styles.contextExplanation}>
          After an Airbyte sync job has completed, the following jobs will run.
        </div>
        <img src="/images/octavia/worker.png" alt="An octopus wearing a hard hat, tools at the ready" />
        No transformations
      </div>
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
