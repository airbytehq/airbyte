import React from "react";

import { Link } from "components";

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
            <Link to={item.to} $clear className={styles.item}>
              {item.label}
            </Link>
          ) : (
            <span className={styles.unlinked} key={index}>
              {item.label}
            </span>
          )}
          {index !== data.length - 1 && <span> / </span>}
        </span>
      ))}
    </div>
  );
};
