import classnames from "classnames";
import React from "react";
import { useIntl } from "react-intl";

import { Input } from "components/ui/Input";

import styles from "./CatalogTreeSearch.module.scss";

interface CatalogTreeSearchProps {
  onSearch: (value: string) => void;
}

export const CatalogTreeSearch: React.FC<CatalogTreeSearchProps> = ({ onSearch }) => {
  const isNewStreamsTableEnabled = process.env.REACT_APP_NEW_STREAMS_TABLE ?? false;

  const { formatMessage } = useIntl();

  const searchStyles = classnames({
    [styles.searchContentNew]: isNewStreamsTableEnabled,
    [styles.searchContent]: !isNewStreamsTableEnabled,
  });

  return (
    <div className={searchStyles}>
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
