import { createContext, useContext, useState } from "react";

import { AirbyteCatalog } from "core/request/AirbyteClient";

// @ts-expect-error Default value provided at implementation
const CatalogContext = createContext<ReturnType<typeof useCatalogState>>();

export const useCatalogState = () => {
  const [catalog, setCatalog] = useState<AirbyteCatalog>();

  return {
    catalog,
    setCatalog,
  };
};

export const useCatalogContext = () => useContext(CatalogContext);

export const CatalogProvider: React.FC = ({ children }) => {
  return <CatalogContext.Provider value={useCatalogContext()}>{children}</CatalogContext.Provider>;
};
