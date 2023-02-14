import classNames from "classnames";
import { PropsWithChildren } from "react";

import { FlexContainer } from "components/ui/Flex";

import { isCloudApp } from "utils/app";

import styles from "./FormPageContent.module.scss";

interface FormPageContentProps {
  big?: boolean;
}

const FormPageContent: React.FC<PropsWithChildren<FormPageContentProps>> = ({ big, children }) => (
  <FlexContainer
    direction="column"
    gap="xl"
    className={classNames(styles.container, {
      [styles.big]: big,
      [styles.cloud]: isCloudApp(),
    })}
  >
    {children}
  </FlexContainer>
);

export default FormPageContent;
