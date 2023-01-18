import { FormattedMessage } from "react-intl";

import styles from "./Separator.module.scss";
export const Separator: React.FC = () => {
  return (
    <div className={styles.separator}>
      <FormattedMessage id="login.oauth.or" />
    </div>
  );
};
