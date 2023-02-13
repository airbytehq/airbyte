import React from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useExperiment } from "hooks/services/Experiment";

import { Separator } from "./components/Separator";
import { Disclaimer, SignupForm } from "./components/SignupForm";
import { SimpleLeftSide } from "./components/SimpleLeftSide/SimpleLeftSide";
import SpecialBlock from "./components/SpecialBlock";
import styles from "./SignupPage.module.scss";
import { OAuthLogin } from "../OAuthLogin";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const SignupPage: React.FC<SignupPageProps> = ({ highlightStyle }) => {
  useTrackPage(PageTrackingCodes.SIGNUP);
  const isSimpleLeftSide = useExperiment("authPage.signup.simplifyLeftSide", false);

  if (isSimpleLeftSide) {
    return <SimpleLeftSide />;
  }
  return (
    <FlexContainer direction="column" gap="xl">
      <HeadTitle titles={[{ id: "login.signup" }]} />
      <Heading as="h1" size="xl" className={styles.title}>
        <FormattedMessage
          id="login.activateAccess"
          values={{
            hl: (hl: React.ReactNode) => (
              <span className={styles.highlight} style={highlightStyle}>
                {hl}
              </span>
            ),
          }}
        />
      </Heading>
      <SpecialBlock />

      <OAuthLogin />
      <Separator />
      <SignupForm />
      <Disclaimer />
    </FlexContainer>
  );
};

export default SignupPage;
