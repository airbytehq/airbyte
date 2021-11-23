import { useMemo } from "react";
import {
  useHistory,
  useLocation,
  useParams,
  useRouteMatch,
} from "react-router";
import { match } from "react-router-dom";

import queryString from "query-string";
import { Location, LocationDescriptor, Path, History } from "history";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function useRouter<T = any, L = any>(): {
  query: T;
  pathname: string;
  location: Location<L>;
  push(path: Path, state?: History.UnknownFacade | null | undefined): void;
  push(location: LocationDescriptor): void;
  replace(path: Path, state?: History.UnknownFacade | null | undefined): void;
  replace(location: LocationDescriptor): void;
  history: History;
  match: match<History.UnknownFacade>;
} {
  const params = useParams();
  const location = useLocation<L>();
  const history = useHistory();
  const match = useRouteMatch();
  const query = useMemo<T>(
    () =>
      ({
        ...queryString.parse(location.search), // Convert string to object
        ...params,
      } as T),
    [params, location.search]
  );

  return useMemo(() => {
    return {
      push: history.push,
      replace: history.replace,
      pathname: location.pathname,
      query,
      match,
      location,
      history,
    };
  }, [match, location, history, query]);
}

export default useRouter;
