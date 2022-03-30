import { QueryClient, QueryClientProvider } from "react-query";
import React from "react";

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
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

export { StoreProvider };
