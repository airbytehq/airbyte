import classNames from "classnames";
import { PropsWithChildren } from "react";

import styles from "./FormPageContent.module.scss";

interface FormPageContentProps {
  big?: boolean;
}

const FormPageContent: React.FC<PropsWithChildren<FormPageContentProps>> = ({ big, children }) => (
  <div className={classNames(styles.container, { [styles.big]: big })}>{children}</div>
);

export default FormPageContent;
