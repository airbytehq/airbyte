import queryString from "query-string";
import { useMemo } from "react";
import { useLocation } from "react-router-dom";

import { SortOrderEnum } from "../components/EntityTable/types";

interface UseQueryResult {
  from?: string;
  id?: string;
  mode?: string;
  oobCode?: string;
  order?: SortOrderEnum;
  sortBy?: string;
}

export const useQuery = (): UseQueryResult => {
  const location = useLocation();
  return useMemo(() => queryString.parse(location.search), [location.search]);
};
