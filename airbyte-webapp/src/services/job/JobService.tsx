import { useMutation, useQuery, useQueryClient } from "react-query";

import { useConfig } from "config";
import { JobsService } from "core/domain/job/JobsService";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useInitService } from "services/useInitService";

import {
  JobDebugInfoRead,
  JobInfoRead,
  JobListRequestBody,
  JobReadList,
  Pagination,
} from "../../core/request/AirbyteClient";
import { useSuspenseQuery } from "../connector/useSuspenseQuery";

export const jobsKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobsKeys.all, "list"] as const,
  list: (filters: string, includingJobId?: number, pagination?: Pagination) =>
    [...jobsKeys.lists(), { filters, includingJobId, pagination }] as const,
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
  const result = useQuery(
    jobsKeys.list(listParams.configId, listParams.includingJobId, listParams.pagination),
    () => service.list(listParams),
    {
      refetchInterval: 2500, // every 2,5 seconds,
      keepPreviousData: true,
      suspense: true,
    }
  );
  // cast to JobReadList because (suspense: true) means we will never get undefined
  const jobReadList = result.data as JobReadList;
  return { jobs: jobReadList.jobs, totalJobCount: jobReadList.totalJobCount, isPreviousData: result.isPreviousData };
};

export const useGetJob = (id: number, enabled = true) => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.detail(id), () => service.get(id), {
    refetchInterval: 2500, // every 2,5 seconds,
    enabled,
  });
};

export const useGetDebugInfoJob = (
  id: number,
  enabled = true,
  refetchWhileRunning = false
): JobDebugInfoRead | undefined => {
  const service = useGetJobService();

  return useSuspenseQuery(jobsKeys.getDebugInfo(id), () => service.getDebugInfo(id), {
    refetchInterval: !refetchWhileRunning
      ? false
      : (data) => {
          // If refetchWhileRunning was true, we keep refetching debug info (including logs), while the job is still
          // running or hasn't ended too long ago. We need some time after the last attempt has stopped, since logs
          // keep incoming for some time after the job has already been marked as finished.
          const lastAttemptEndTimestamp =
            data?.attempts.length && data.attempts[data.attempts.length - 1].attempt.endedAt;
          // While no attempt ended timestamp exists yet (i.e. the job is still running) or it hasn't ended
          // more than 2 minutes (2 * 60 * 1000ms) ago, keep refetching
          return lastAttemptEndTimestamp && Date.now() - lastAttemptEndTimestamp * 1000 > 2 * 60 * 1000 ? false : 2500;
        },
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
