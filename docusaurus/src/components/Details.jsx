import { useLocation } from "@docusaurus/router";
import classNames from "classnames";
import React from "react";
import styles from "./Details.module.css";

export const Details = ({ className, ...rest }) => {
  const location = useLocation();
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef(null);

  const [summary, ...content] = rest.children;

  React.useEffect(() => {
    const detailsHeaderId = ref.current.previousElementSibling.id
    const contentIds = [...rest.children]
      .map((element) => {
        if (element.props.id) {
          return `#${element.props.id}`;
        }
      })
      .filter(Boolean);

    if (contentIds.includes(location.hash) || location.hash === `#${detailsHeaderId}`) {
      setOpen(true);
    } else {
      setOpen(false);
    }
  }, [location.hash, rest.children, ref.current]);

  return (
    <details
      open={open}
      ref={ref}
      className={classNames(
        className,
        "alert",
        "alert--info",
        styles.details
      )}
      {...rest}
    >
      {summary}
      <div className={classNames(styles.detailsContent)}>{content}</div>
    </details>
  );
};
