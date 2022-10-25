import classNames from "classnames";
import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { ReactComponent as BowtieHalf } from "./bowtie-half.svg";
import styles from "./EmptyResourceListView.module.scss";

interface EmptyResourceListViewProps {
  buttonLabel: string;
  resourceType: "connections" | "destinations" | "sources";
  onCreateClick: () => void;
}

export const EmptyResourceListView: React.FC<EmptyResourceListViewProps> = ({
  resourceType,
  onCreateClick,
  buttonLabel,
}) => {
  const { headingMessageId, singularResourceType } = useMemo(() => {
    const singularResourceType = resourceType.substring(0, resourceType.length - 1);
    const baseMessageId = resourceType === "connections" ? singularResourceType : resourceType;

    const headingMessageId = `${baseMessageId}.description`;

    return { headingMessageId, singularResourceType };
  }, [resourceType]);

  return (
    <div className={styles.container}>
      <Text as="h2" size="lg" centered className={styles.heading}>
        <FormattedMessage id={headingMessageId} />
      </Text>
      <div className={classNames(styles.container, styles.illustration)}>
        {resourceType !== "destinations" && (
          <BowtieHalf aria-hidden="true" className={classNames(styles.bowtie, styles.left)} />
        )}
        {resourceType !== "sources" && (
          <BowtieHalf aria-hidden="true" className={classNames(styles.bowtie, styles.right)} />
        )}
        <img
          className={styles.octavia}
          src={`/images/octavia/empty-${resourceType}.png`}
          alt=""
          resource={resourceType}
        />
      </div>
      <Button onClick={onCreateClick} size="lg" data-id={`new-${singularResourceType}`}>
        {buttonLabel}
      </Button>
    </div>
  );
};
