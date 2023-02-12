import classNames from "classnames";
import { PropsWithChildren } from "react";
import { Link as ReactRouterLink, To } from "react-router-dom";

import styles from "./Link.module.scss";

interface LinkProps {
  className?: string;
  opensInNewTab?: boolean;
}

interface InternalLinkProps extends LinkProps {
  to: To;
}

export const Link: React.FC<PropsWithChildren<InternalLinkProps>> = ({
  children,
  className,
  to,
  opensInNewTab = false,
  ...props
}) => {
  return (
    <ReactRouterLink
      {...props}
      className={classNames(styles.link, className)}
      rel={opensInNewTab ? "noopener noreferrer" : undefined}
      target={opensInNewTab ? "_blank" : "_self"}
      to={to}
    >
      {children}
    </ReactRouterLink>
  );
};

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
