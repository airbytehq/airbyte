import {
  QueryObserverSuccessResult,
  UseMutateAsyncFunction,
  useMutation,
  useQuery,
  useQueryClient,
} from "react-query";

import { useConfig } from "config";
import { useDefaultRequestMiddlewares } from "packages/cloud/services/useDefaultRequestMiddlewares";
import { useInitService } from "packages/cloud/services/useInitService";
import { JobsService, ListParams } from "core/domain/job/JobsService";
import { JobDetails, JobListItem } from "core/domain/job/Job";

export const jobsKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobsKeys.all, "list"] as const,
  list: (filters: string) => [...jobsKeys.lists(), { filters }] as const,
  detail: (jobId: string | number) =>
    [...jobsKeys.all, "details", jobId] as const,
  cancel: (jobId: string) => [...jobsKeys.all, "cancel", jobId] as const,
};

function useGetJobService(): JobsService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new JobsService(apiUrl, requestAuthMiddleware), [
    apiUrl,
    requestAuthMiddleware,
  ]);
}

export const useListJobs = (listParams: ListParams): JobListItem[] => {
  const service = useGetJobService();
  return (useQuery(
    jobsKeys.list(listParams.configId),
    () => service.list(listParams),
    {
      refetchInterval: 2500, // every 2,5 seconds,
    }
  ) as QueryObserverSuccessResult<{ jobs: JobListItem[] }>).data.jobs;
};

export const useGetJob = (id: string | number): JobDetails => {
  const service = useGetJobService();

  return (useQuery(jobsKeys.detail(id), () => service.get(id), {
    refetchInterval: 2500, // every 2,5 seconds,
  }) as QueryObserverSuccessResult<JobDetails>).data;
};

export const useCancelJob = (): UseMutateAsyncFunction<
  JobDetails,
  Error,
  string | number
> => {
  const service = useGetJobService();
  const queryClient = useQueryClient();

  return useMutation<JobDetails, Error, string | number>(
    (id: string | number) => service.cancel(id),
    {
      onSuccess: (data) => {
        queryClient.setQueryData(jobsKeys.detail(data.job.id), data);
      },
    }
  ).mutateAsync;
};
