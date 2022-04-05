import { QueryClient, QueryClientProvider } from "react-query";
import React from "react";
import { CacheProvider } from "rest-hooks";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      suspense: true,
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
  },
});

const StoreProvider: React.FC = ({ children }) => (
  <CacheProvider>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  </CacheProvider>
);

export { StoreProvider };
