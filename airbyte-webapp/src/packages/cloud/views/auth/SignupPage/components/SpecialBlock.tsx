import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./SpecialBlock.module.scss";

const SpecialBlock: React.FC = () => {
  return (
    <h6 className={styles.text}>
      <FormattedMessage
        id="login.activateAccess.subtitle"
        values={{
          launch: (special: React.ReactNode) => <span className={styles.launch}>{special}</span>,
          sum: (sum: React.ReactNode) => <span className={styles.sum}>{sum}</span>,
        }}
      />
    </h6>
  );
};

export default SpecialBlock;
