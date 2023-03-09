import classNames from "classnames";
import { PropsWithChildren } from "react";

import { isCloudApp } from "utils/app";

import styles from "./FormPageContent.module.scss";

interface FormPageContentProps {
  big?: boolean;
}

const FormPageContent: React.FC<PropsWithChildren<FormPageContentProps>> = ({ big, children }) => (
  <div
    className={classNames(styles.container, {
      [styles.big]: big,
      [styles.cloud]: isCloudApp(),
    })}
  >
    {children}
  </div>
);

export default FormPageContent;
