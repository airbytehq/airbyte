import { faGoogle } from "@fortawesome/free-brands-svg-icons";
import { faCheckCircle, faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";

import styles from "./SimpleLeftSide.module.scss";
import { OAuthLogin } from "../../../OAuthLogin";
import { Disclaimer, SignupForm } from "../SignupForm";

const Detail: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <FlexContainer gap="sm" alignItems="center" className={styles.detailTextContainer}>
      <FontAwesomeIcon icon={faCheckCircle} className={styles.checkIcon} />
      {children}
    </FlexContainer>
  );
};
export const SimpleLeftSide: React.FC = () => {
  const [showOauth, setShowOauth] = useState(true);
  return (
    <FlexContainer direction="column" gap="xl">
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <Heading as="h1" centered>
        <FormattedMessage id="signup.title" />
      </Heading>

      <FlexContainer className={styles.detailsContainer} alignItems="center">
        <Detail>
          <FormattedMessage id="signup.details.noCreditCard" />
        </Detail>
        <Detail>
          <FormattedMessage id="signup.details.instantSetup" />
        </Detail>
        <Detail>
          <FormattedMessage id="signup.details.freeTrial" />
        </Detail>
      </FlexContainer>
      {showOauth ? <OAuthLogin isSignUpPage /> : <SignupForm />}

      {showOauth ? (
        <Button
          onClick={() => setShowOauth(false)}
          variant="clear"
          size="sm"
          icon={<FontAwesomeIcon icon={faEnvelope} />}
        >
          <FormattedMessage id="signup.method.email" />
        </Button>
      ) : (
        <Button onClick={() => setShowOauth(true)} variant="clear" size="sm" icon={<FontAwesomeIcon icon={faGoogle} />}>
          <FormattedMessage id="signup.method.oauth" />
        </Button>
      )}

      <Disclaimer />
    </FlexContainer>
  );
};
