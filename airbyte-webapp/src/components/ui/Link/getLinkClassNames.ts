import classNames from "classnames";

import { LinkProps } from "./Link";
import styles from "./Link.module.scss";

type GetClassNamesArgs = Pick<LinkProps, "variant"> & {
  className?: string;
};

export const getLinkClassNames = ({ className, variant }: GetClassNamesArgs) => {
  return classNames(styles.link, { [styles["link--primary"]]: variant === "primary" }, className);
};
