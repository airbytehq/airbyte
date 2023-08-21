import { useState, useEffect } from "react";

const PAGE_CONFIG = "daspire-page-config";

type NewValue<T> = {
  [P in keyof T]?: T[P];
};

interface Iprops {
  pageSize: number;
}

interface PageConfig {
  connection: Iprops;
  source: Iprops;
  destination: Iprops;
}

const defaultPageSize = {
  pageSize: 10,
};

const defaultConfig: PageConfig = {
  connection: defaultPageSize,
  source: defaultPageSize,
  destination: defaultPageSize,
};

export const usePageConfig = (): [
  PageConfig,
  (page: keyof PageConfig, newSize: number) => void,
  (page: keyof PageConfig, field: keyof Iprops, newValue: NewValue<Iprops>) => void
] => {
  const storedPageConfig = localStorage.getItem(PAGE_CONFIG);
  const [pageConfig, setPageConfig] = useState<PageConfig>(
    storedPageConfig ? JSON.parse(storedPageConfig) : defaultConfig
  );

  // Update local storage whenever pageConfig changes
  useEffect(() => {
    localStorage.setItem(PAGE_CONFIG, JSON.stringify(pageConfig));
  }, [pageConfig]);

  // Function to update a specific page size
  const updatePageSize = (page: keyof PageConfig, newSize: number) => {
    setPageConfig((prevPageConfig) => ({
      ...prevPageConfig,
      [page]: {
        pageSize: newSize,
      },
    }));
  };

  // Function to update all field
  const updatePageConfig = (page: keyof PageConfig, field: keyof Iprops, newValue: NewValue<Iprops>) => {
    setPageConfig((prevPageConfig) => ({
      ...prevPageConfig,
      [page]: {
        [field]: newValue,
      },
    }));
  };

  return [pageConfig, updatePageSize, updatePageConfig];
};
