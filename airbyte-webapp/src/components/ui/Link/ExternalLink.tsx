import classNames from "classnames";
import { PropsWithChildren } from "react";

import { LinkProps } from "./Link";
import styles from "./Link.module.scss";

interface ExternalLinkProps extends LinkProps {
  href: string;
}

export const ExternalLink: React.FC<PropsWithChildren<ExternalLinkProps>> = ({
  children,
  className,
  opensInNewTab = true,
  href,
  ...props
}) => {
  return (
    <a
      {...props}
      className={classNames(styles.link, className)}
      href={href}
      rel={opensInNewTab ? "noopener noreferrer" : undefined}
      target={opensInNewTab ? "_blank" : "_self"}
    >
      {children}
    </a>
  );
};
