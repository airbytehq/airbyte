import queryString from "query-string";
import { useMemo } from "react";
import { useLocation } from "react-router-dom";

export const useQuery = () => {
  const location = useLocation();
  return useMemo(() => queryString.parse(location.search), [location.search]);
};
