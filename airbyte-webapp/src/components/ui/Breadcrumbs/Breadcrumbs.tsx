import React from "react";
import { Link } from "react-router-dom";

import styles from "./Breadcrumbs.module.scss";

export interface BreadcrumbsDataItem {
  label: string;
  to?: string;
}

interface BreadcrumbsProps {
  data: BreadcrumbsDataItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ data }) => {
  return (
    <div className={styles.container}>
      {data.map((item, index) => (
        <span key={index}>
          {item.to ? (
            <Link to={item.to} className={styles.item}>
              {item.label}
            </Link>
          ) : (
            <span className={styles["item--unlinked"]} key={index}>
              {item.label}
            </span>
          )}
          {index !== data.length - 1 && <span> / </span>}
        </span>
      ))}
    </div>
  );
};
