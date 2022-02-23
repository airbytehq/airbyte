import { useFetcher } from "rest-hooks";

import JobResource, { Job } from "core/resources/Job";

type JobService = {
  cancelJob: (jobId: number | string) => Promise<Job>;
};

const useJob = (): JobService => {
  const cancelJobRequest = useFetcher(JobResource.cancelShape());

  const cancelJob = async (jobId: number | string) => {
    return await cancelJobRequest(
      {
        id: jobId,
      },
      {}
    );
  };

  return {
    cancelJob,
  };
};

export default useJob;
