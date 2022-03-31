import { QueryClient, QueryClientProvider } from "react-query";
import React from "react";
import { CacheProvider } from "rest-hooks";
import { ReactQueryDevtools } from "react-query/devtools";

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
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools initialIsOpen={false} />
      {children}
    </QueryClientProvider>
  </CacheProvider>
);

export { StoreProvider };
