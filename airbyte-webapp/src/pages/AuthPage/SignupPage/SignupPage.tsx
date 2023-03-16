import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import HeadTitle from "components/HeadTitle";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";

// import { Link } from "../../../components/Link";
import { FormHeaderSection } from "pages/AuthPage/components/FormHeaderSection";

import { RoutePaths } from "../../routePaths";
import { SignupForm } from "./components/SignupForm";
import styles from "./SignupPage.module.scss";

interface SignupPageProps {
  highlightStyle?: React.CSSProperties;
}

const ImageContent = styled.div`
  position: absolute;
  top: 200px;
  left: 70px;
`;

const LogoHeader = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  padding: 30px;
`;

const LogoText = styled.div`
  font-weight: bold;
  font-size: 16px;
  color: white;
  padding-left: 10px;
`;

const SignupPage: React.FC<SignupPageProps> = () => {
  useTrackPage(PageTrackingCodes.SIGNUP);
  const { formatMessage } = useIntl();
  return (
    <div className={styles.container}>
      <HeadTitle titles={[{ id: "signup.pageTitle" }]} />
      <div className={styles.informationContent}>
        <ImageContent>
          <img src="/SignupCover.png" alt="cover" style={{ maxWidth: "80%", height: "auto", objectFit: "cover" }} />
        </ImageContent>
        <LogoHeader>
          <img src="/daspireWhiteLogo.svg" alt="logo" width={40} />
          <LogoText>
            <FormattedMessage id="daspire" />
          </LogoText>
        </LogoHeader>
        <div className={styles.context}>
          <div className={styles.titleContent}>
            <span className={styles.titleText}>
              <FormattedMessage id="signup.Title" />
            </span>
          </div>
          <div className={styles.firstListItem}>
            <img src="/daspireList1.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List1" />
            </span>
          </div>

          <div className={styles.listItem}>
            <img src="/daspireList2.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List2" />
            </span>
          </div>

          <div className={styles.listItem}>
            <img src="/daspireList6.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List6" />
            </span>
          </div>

          <div className={styles.listItem}>
            <img src="/daspireList3.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List3" />
            </span>
          </div>

          <div className={styles.listItem}>
            <img src="/daspireList4.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List4" />
            </span>
          </div>

          <div className={styles.listItem}>
            <img src="/daspireList5.svg" alt="logo" width={20} />
            <span className={styles.text}>
              <FormattedMessage id="signup.List5" />
            </span>
          </div>
        </div>
      </div>
      <div className={styles.rightContent}>
        <FormHeaderSection
          link={`/${RoutePaths.Signin}`}
          buttonText={formatMessage({ id: "signup.siginButton" })}
          text={formatMessage({ id: "signup.haveAccount" })}
        />
        {/* <SigninButtonContent>
          <SigninText>
            <FormattedMessage id="signup.haveAccount" />
          </SigninText>
          <SigninButton>
            <Link $clear to={`/${RoutePaths.Signin}`}>
              <FormattedMessage id="signup.siginButton" />
            </Link>
          </SigninButton>
        </SigninButtonContent> */}
        {/* <SignupFormContainer> */}
        <SignupForm />
        {/* </SignupFormContainer> */}
      </div>
    </div>
  );
};

export default SignupPage;
