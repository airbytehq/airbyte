import React from "react";
import { useIntl } from "react-intl";

import { Input } from "components/ui/Input";

import styles from "./CatalogTreeSearch.module.scss";

interface CatalogTreeSearchProps {
  onSearch: (value: string) => void;
}

export const CatalogTreeSearch: React.FC<CatalogTreeSearchProps> = ({ onSearch }) => {
  const { formatMessage } = useIntl();

  return (
    <div className={styles.searchContent}>
      <Input
        className={styles.searchInput}
        placeholder={formatMessage({
          id: `form.nameSearch`,
        })}
        onChange={(e) => onSearch(e.target.value)}
      />
    </div>
  );
};
