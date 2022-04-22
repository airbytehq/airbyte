import { UseMutateAsyncFunction, useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { JobDetails, JobListItem, JobDebugInfoDetails } from "core/domain/job/Job";
import { JobsService, ListParams } from "core/domain/job/JobsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

import { useSuspenseQuery } from "../connector/useSuspenseQuery";

export const jobsKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobsKeys.all, "list"] as const,
  list: (filters: string) => [...jobsKeys.lists(), { filters }] as const,
  detail: (jobId: string | number) => [...jobsKeys.all, "details", jobId] as const,
  getDebugInfo: (jobId: string | number) => [...jobsKeys.all, "getDebugInfo", jobId] as const,
  cancel: (jobId: string) => [...jobsKeys.all, "cancel", jobId] as const,
};

function useGetJobService(): JobsService {
  const { apiUrl } = useConfig();

  const requestAuthMiddleware = useDefaultRequestMiddlewares();

  return useInitService(() => new JobsService(apiUrl, requestAuthMiddleware), [apiUrl, requestAuthMiddleware]);
}

export const useListJobs = (listParams: ListParams): JobListItem[] => {
  const service = useGetJobService();
  return useSuspenseQuery(jobsKeys.list(listParams.configId), () => service.list(listParams), {
    refetchInterval: 2500, // every 2,5 seconds,
  }).jobs;
};

export const useGetJob = (id: string | number): JobDetails => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.detail(id), () => service.get(id), {
    refetchInterval: 2500, // every 2,5 seconds,
  });
};

export const useGetDebugInfoJob = (id: string | number): JobDebugInfoDetails => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.getDebugInfo(id), () => service.getDebugInfo(id), {
    refetchInterval: false,
  });
};

export const useCancelJob = (): UseMutateAsyncFunction<JobDetails, Error, string | number> => {
  const service = useGetJobService();
  const queryClient = useQueryClient();

  return useMutation<JobDetails, Error, string | number>((id: string | number) => service.cancel(id), {
    onSuccess: (data) => {
      queryClient.setQueryData(jobsKeys.detail(data.job.id), data);
    },
  }).mutateAsync;
};
