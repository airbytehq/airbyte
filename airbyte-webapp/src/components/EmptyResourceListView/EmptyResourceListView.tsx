import classNames from "classnames";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/base/Button";
import { Text } from "components/base/Text";

import styles from "./EmptyResourceListView.module.scss";

interface EmptyResourceListViewProps {
  resourceType: "connections" | "destinations" | "sources";
  onCreateClick: () => void;
}

export const EmptyResourceListView: React.FC<EmptyResourceListViewProps> = ({ resourceType, onCreateClick }) => {
  const { headingMessageId, buttonMessageId, singularResourceType } = useMemo(() => {
    const singularResourceType = resourceType.substring(0, resourceType.length - 1);
    const baseMessageId = resourceType === "connections" ? singularResourceType : resourceType;

    const headingMessageId = `${baseMessageId}.description`;
    const buttonMessageId = `${baseMessageId}.new${
      singularResourceType.substring(0, 1).toUpperCase() + singularResourceType.substring(1)
    }`;

    return { headingMessageId, buttonMessageId, singularResourceType };
  }, [resourceType]);

  return (
    <div className={styles.container}>
      <Text as="h2" size="lg" centered className={styles.heading}>
        <FormattedMessage id={headingMessageId} />
      </Text>
      <div className={classNames(styles.container, styles.illustration)}>
        {resourceType !== "destinations" && (
          <img src="/images/bowtie-half.svg" alt="Left Bowtie" className={classNames(styles.bowtie, styles.left)} />
        )}
        {resourceType !== "sources" && (
          <img src="/images/bowtie-half.svg" alt="Right Bowtie" className={classNames(styles.bowtie, styles.right)} />
        )}
        <img
          className={styles.octavia}
          src={`/images/octavia/empty-${resourceType}.png`}
          alt="Octavia"
          resource={resourceType}
        />
      </div>
      <Button onClick={onCreateClick} size="lg" data-id={`new-${singularResourceType}`}>
        <FormattedMessage id={buttonMessageId} />
      </Button>
    </div>
  );
};
