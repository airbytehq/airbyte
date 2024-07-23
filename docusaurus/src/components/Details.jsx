import { useLocation } from "@docusaurus/router";
import classNames from "classnames";
import React from "react";
import styles from "./Details.module.css";

export const Details = ({ className, children, ...rest }) => {
  const location = useLocation();
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef(null);

  const items = React.Children.toArray(children);
  const summary = items.find((item) => React.isValidElement(item) && item.type === "summary");
  const content = items.filter((item) => React.isValidElement(item) && item.type !== "summary");


  React.useEffect(() => {
    const detailsHeaderId = ref.current?.previousElementSibling?.id
    const contentIds = content
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
  }, [location.hash, content, summary, ref.current]);

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
