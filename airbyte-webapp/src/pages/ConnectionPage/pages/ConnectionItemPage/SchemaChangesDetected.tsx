import classNames from "classnames";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { SchemaChange } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useRefreshSourceSchemaWithConfirmationOnDirty } from "views/Connection/ConnectionForm/components/refreshSourceSchemaWithConfirmationOnDirty";

import styles from "./SchemaChangesDetected.module.scss";

export const useSchemaChanges = (schemaChange: SchemaChange) => {
  const isSchemaChangesFeatureEnabled = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES === "true" ?? false;

  const hasSchemaChanges = isSchemaChangesFeatureEnabled && schemaChange !== SchemaChange.no_change;
  const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
  const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;

  return {
    schemaChange,
    hasSchemaChanges,
    hasBreakingSchemaChange,
    hasNonBreakingSchemaChange,
  };
};

export const SchemaChangesDetected: React.FC = () => {
  const {
    connection: { schemaChange },
    schemaRefreshing,
    schemaHasBeenRefreshed,
  } = useConnectionEditService();

  const { hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);
  const refreshSchema = useRefreshSourceSchemaWithConfirmationOnDirty(false);

  if (schemaHasBeenRefreshed) {
    return null;
  }

  const schemaChangeClassNames = {
    [styles.breaking]: hasBreakingSchemaChange,
    [styles.nonBreaking]: hasNonBreakingSchemaChange,
  };

  return (
    <div className={classNames(styles.container, schemaChangeClassNames)}>
      <Text size="lg">
        <FormattedMessage id={`connection.schemaChange.${hasBreakingSchemaChange ? "breaking" : "nonBreaking"}`} />
      </Text>
      <Button onClick={() => refreshSchema()} isLoading={schemaRefreshing}>
        <FormattedMessage id="connection.schemaChange.reviewCTA" />
      </Button>
    </div>
  );
};
