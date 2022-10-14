import { faPlus, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, Form, Formik, FieldArray, FieldProps } from "formik";
import { Link } from "react-router-dom";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { Input } from "components/ui/Input";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { RoutePaths } from "pages/routePaths";

import styles from "./DbtCloudTransformationsCard.module.scss";

interface Transformation {
  project: string;
  job: string;
}

// This won't be used by the first prototype, but it is the UI specced in
// follow-up designs which can support multiple integrations; it's also a small,
// self-contained set of components and scss which will only trivially affect
// bundle size.
// eslint-disable-next-line: @typescript-eslint/no-usused-vars @typescript-eslint/ban-ts-comment
// @ts-ignore: no unused locals
const TransformationsList = ({
  className,
  transformations,
}: {
  className?: string;
  transformations: Transformation[];
}) => {
  const onSubmit = (fields: { transformations: Transformation[] }) => {
    console.info(`Saving with this job list: ${JSON.stringify(fields)}`);
  };

  const transformationKey = (t: Transformation, i: number) => `${i}:${t.project}/${t.job}`;

  return (
    <div className={classNames(className, styles.emptyListContent)}>
      <p className={styles.contextExplanation}>After an Airbyte sync job has completed, the following jobs will run</p>
      {transformations.length ? (
        <Formik
          onSubmit={onSubmit}
          initialValues={{ transformations }}
          render={({ values }) => (
            <Form className={styles.transformationListForm}>
              <FieldArray
                name="transformations"
                render={(arrayHelpers) =>
                  values.transformations.map((t, i) => (
                    <TransformationListItem
                      key={transformationKey(t, i)}
                      transformationIndex={i}
                      deleteTransformation={() => arrayHelpers.remove(i)}
                    />
                  ))
                }
              />
              <div className={styles.transformationListButtonGroup}>
                <Button className={styles.transformationListButton} type="reset" variant="secondary">
                  Cancel
                </Button>
                <Button className={styles.transformationListButton} type="submit" variant="primary">
                  Save changes
                </Button>
              </div>
            </Form>
          )}
        />
      ) : (
        <>
          <img src="/images/octavia/worker.png" alt="An octopus wearing a hard hat, tools at the ready" />
          No transformations
        </>
      )}
    </div>
  );
};

const TransformationListItem = ({
  transformationIndex,
  deleteTransformation,
}: {
  transformationIndex: number;
  deleteTransformation: () => void;
}) => {
  return (
    <Card className={styles.transformationListItem}>
      <div className={styles.transformationListItemIntegrationName}>
        <img src="/images/external/dbt-bit_tm.png" alt="dbt logo" />
        dbt Cloud transform
      </div>
      <div className={styles.transformationListItemInputGroup}>
        <div className={styles.transformationListItemInput}>
          <Field name={`transformations.${transformationIndex}.project`}>
            {({ field }: FieldProps<string>) => <Input {...field} type="text" placeholder="Project name" />}
          </Field>
        </div>
        <div className={styles.transformationListItemInput}>
          <Field name={`transformations.${transformationIndex}.job`}>
            {({ field }: FieldProps<string>) => <Input {...field} type="text" placeholder="Job name" />}
          </Field>
        </div>
        <button type="button" className={styles.transformationListItemDelete} onClick={deleteTransformation}>
          <FontAwesomeIcon icon={faXmark} />
        </button>
      </div>
    </Card>
  );
};

const NoDbtIntegration = ({ className, workspaceId }: { className: string; workspaceId: string }) => {
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
  /* const transformations: Transformation[] = []; */
  const transformations: Transformation[] = [
    { project: "Project #1", job: "Job #1" },
    { project: "Project #1", job: "Job #2" },
    { project: "Project #1", job: "Job #3" },
  ];

  const { workspaceId } = useCurrentWorkspace();
  const hasDbtIntegration = true;
  /* const hasDbtIntegration = false; */

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
      {hasDbtIntegration ? (
        <TransformationsList transformations={transformations} className={styles.cloudTransformationsListContainer} />
      ) : (
        <NoDbtIntegration className={styles.cloudTransformationsListContainer} workspaceId={workspaceId} />
      )}
    </Card>
  );
};
