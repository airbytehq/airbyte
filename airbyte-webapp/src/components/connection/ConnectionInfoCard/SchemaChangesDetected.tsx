import classNames from "classnames";
import { FormattedMessage } from "react-intl";
import { useLocation, useNavigate } from "react-router-dom";

import { useRefreshSourceSchemaWithConfirmationOnDirty } from "components/connection/ConnectionForm/refreshSourceSchemaWithConfirmationOnDirty";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { useSchemaChanges } from "hooks/connection/useSchemaChanges";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { ConnectionRoutePaths } from "pages/connections/types";

import styles from "./SchemaChangesDetected.module.scss";

export const SchemaChangesDetected: React.FC = () => {
  const {
    connection: { schemaChange },
    schemaRefreshing,
    schemaHasBeenRefreshed,
  } = useConnectionEditService();
  const { hasFormChanges } = useFormChangeTrackerService();

  const { hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);
  const refreshSchema = useRefreshSourceSchemaWithConfirmationOnDirty(hasFormChanges);
  const location = useLocation();
  const navigate = useNavigate();

  if (schemaHasBeenRefreshed) {
    return null;
  }

  const onReviewActionButtonClick: React.MouseEventHandler<HTMLButtonElement> = () => {
    if (!location.pathname.includes(`/${ConnectionRoutePaths.Replication}`)) {
      navigate(ConnectionRoutePaths.Replication);
    }

    refreshSchema();
  };

  const schemaChangeClassNames = {
    [styles.breaking]: hasBreakingSchemaChange,
    [styles.nonBreaking]: hasNonBreakingSchemaChange,
  };

  return (
    <div className={classNames(styles.container, schemaChangeClassNames)} data-testid="schemaChangesDetected">
      <Text size="lg">
        <FormattedMessage id={`connection.schemaChange.${hasBreakingSchemaChange ? "breaking" : "nonBreaking"}`} />
      </Text>
      <Button variant="dark" onClick={onReviewActionButtonClick} isLoading={schemaRefreshing}>
        <FormattedMessage id="connection.schemaChange.reviewAction" />
      </Button>
    </div>
  );
};
