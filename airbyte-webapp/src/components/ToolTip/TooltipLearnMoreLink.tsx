import { FormattedMessage } from "react-intl";

import styles from "./TooltipLearnMoreLink.module.scss";

interface TooltipLearnMoreLinkProps {
  url: string;
}

export const TooltipLearnMoreLink: React.VFC<TooltipLearnMoreLinkProps> = ({ url }) => (
  <div className={styles.container}>
    <a href={url} target="_blank" rel="noreferrer">
      <FormattedMessage id="ui.learnMore" />
    </a>
  </div>
);
