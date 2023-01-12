import { FormattedMessage } from "react-intl";

import { Alert } from "components/ui/Alert/Alert";
import { Text } from "components/ui/Text";

const EnrollLink = () => {
  const onEnrollClick = () => {
    return null;
  };
  return (
    <span
      role="button"
      onClick={(e) => onEnrollClick()}
      onKeyDown={(e) => e.keyCode === 13 && onEnrollClick}
      tabIndex={0}
    >
      <FormattedMessage id="freeConnectorProgram.youCanEnroll.free" />
    </span>
  );
};
export const InlineEnrollmentAlert: React.FC = () => {
  return (
    <Alert variant="blue">
      <Text size="sm">
        <FormattedMessage id="freeConnectorProgram.youCanEnroll" link={EnrollLink} />
      </Text>
    </Alert>
  );
};
