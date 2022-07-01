import queryString from "query-string";
import { useMemo } from "react";
import { useLocation, useNavigate, useParams, Location, To, NavigateOptions } from "react-router-dom";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function useRouter<T = any, P = any>(): {
  query: T;
  params: P;
  pathname: string;
  location: Location;
  push(path: To, state?: NavigateOptions): void;
  replace(path: To, state?: NavigateOptions): void;
} {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const params: any = useParams();
  const location = useLocation();
  const navigate = useNavigate();
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
      params,
      push: navigate,
      replace: (path, state) => navigate(path, { ...state, replace: true }),
      pathname: location.pathname,
      query,
      location,
    };
  }, [navigate, location, query, params]);
}

export default useRouter;
