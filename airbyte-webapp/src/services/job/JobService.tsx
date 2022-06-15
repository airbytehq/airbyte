import { useMutation, useQueryClient } from "react-query";

import { useConfig } from "config";
import { JobsService } from "core/domain/job/JobsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

import { JobDebugInfoRead, JobInfoRead, JobListRequestBody } from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../connector/useSuspenseQuery";

export const jobsKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobsKeys.all, "list"] as const,
  list: (filters: string) => [...jobsKeys.lists(), { filters }] as const,
  detail: (jobId: number) => [...jobsKeys.all, "details", jobId] as const,
  getDebugInfo: (jobId: number) => [...jobsKeys.all, "getDebugInfo", jobId] as const,
  cancel: (jobId: string) => [...jobsKeys.all, "cancel", jobId] as const,
};

function useGetJobService() {
  const config = useConfig();
  const middlewares = useDefaultRequestMiddlewares();
  return useInitService(() => new JobsService(config.apiUrl, middlewares), [config.apiUrl, middlewares]);
}

export const useListJobs = (listParams: JobListRequestBody) => {
  const service = useGetJobService();
  return useSuspenseQuery(jobsKeys.list(listParams.configId), () => service.list(listParams), {
    refetchInterval: 2500, // every 2,5 seconds,
  }).jobs;
};

export const useGetJob = (id: number, enabled = true) => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.detail(id), () => service.get(id), {
    refetchInterval: 2500, // every 2,5 seconds,
    enabled,
  });
};

export const useGetDebugInfoJob = (id: number, enabled = true): JobDebugInfoRead | undefined => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.getDebugInfo(id), () => service.getDebugInfo(id), {
    refetchInterval: false,
    enabled,
  });
};

export const useCancelJob = () => {
  const service = useGetJobService();
  const queryClient = useQueryClient();

  return useMutation<JobInfoRead, Error, number>((id: number) => service.cancel(id), {
    onSuccess: (data) => {
      queryClient.setQueryData(jobsKeys.detail(data.job.id), data);
    },
  }).mutateAsync;
};
