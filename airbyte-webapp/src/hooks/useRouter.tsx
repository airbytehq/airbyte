import queryString from "query-string";
import { useMemo } from "react";
import { useLocation, useNavigate, useParams, To, NavigateOptions } from "react-router-dom";

import { SortOrderEnum } from "../components/EntityTable/types";

interface UseRouterQueryResult {
  from?: string;
  id?: string;
  mode?: string;
  oobCode?: string;
  order?: SortOrderEnum;
  sortBy?: string;
}

export const useRouterQuery = (): UseRouterQueryResult => {
  const params = useParams();
  const location = useLocation();
  return useMemo(
    () => ({
      ...queryString.parse(location.search), // Convert string to object
      ...params,
    }),
    [params, location.search]
  );
};

type UseRouterReplaceInterface = (path: To, state?: NavigateOptions) => void;

export const useRouterReplace = (): UseRouterReplaceInterface => {
  const navigate = useNavigate();
  return (path, state) => navigate(path, { ...state, replace: true });
};
