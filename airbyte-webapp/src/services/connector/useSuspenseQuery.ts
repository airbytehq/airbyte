import { QueryFunction, QueryKey, useQuery, UseQueryOptions } from "react-query";

interface Disabled {
  enabled: false;
}

export function useSuspenseQuery<
  TQueryFnData = unknown,
  TError = unknown,
  TData = TQueryFnData,
  TQueryKey extends QueryKey = QueryKey
>(
  queryKey: TQueryKey,
  queryFn: QueryFunction<TQueryFnData, TQueryKey>,
  options: Readonly<
    Omit<UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>, "queryKey" | "queryFn" | "suspense">
  > = {}
) {
  return useQuery<TQueryFnData, TError, TData, TQueryKey>(queryKey, queryFn, {
    ...options,
    suspense: true,
  }).data as typeof options extends Disabled ? TData | undefined : TData;
}
