import { useLocation } from "react-router-dom";

import { AttemptRead } from "core/request/AirbyteClient";

const PARSE_REGEXP = /^#(?<jobId>\w*)::(?<attemptId>\w*)$/;
// const INITIAL_JOB_PAGE_SIZE = 25;

/**
 * Create and returns a link for a specific job and (optionally) attempt.
 * The returned string is the hash part of a URL.
 */
export const buildAttemptLink = (jobId: number | string, attemptId?: AttemptRead["id"]): string => {
  return `#${jobId}::${attemptId ?? ""}`;
};

/**
 * Parses a hash part of the URL into a jobId and attemptId.
 * This is the reverse function of {@link buildAttemptLink}.
 */
export const parseAttemptLink = (link: string): { jobId?: string; attemptId?: string } => {
  const match = link.match(PARSE_REGEXP);
  if (!match) {
    return {};
  }
  return {
    jobId: match.groups?.jobId,
    attemptId: match.groups?.attemptId,
  };
};

/**
 * Returns the information about which attempt was linked to from the hash if available.
 */
export const useAttemptLink = () => {
  const { hash } = useLocation();
  return parseAttemptLink(hash);
};

// export const useLinkedJobOffset = (jobs: JobWithAttemptsRead[], initialListParams: number) => {
//   const { jobs } = useListJobs({ ...listParams, pagination: { pageSize: jobPageSize } });

//   const { jobId: linkedJobId } = useAttemptLink();
//   const linkedJobIdNum = Number(linkedJobId);

//   // if there is no linked job ID or it is not a valid number, do nothing
//   if (isNaN(linkedJobIdNum)) {
//     return null;
//   }

//   // get all job ids, filtering out any jobs that don't have an id
//   const jobIds = jobs.flatMap((job) => (job.job?.id ? [job.job?.id] : []));
//   const minJobId = Math.min(...jobIds);

//   if (linkedJobIdNum < minJobId && moreJobPagesAvailable) {
//     // setJobPageSize((prevJobPageSize) => {
//     //   console.log(
//     //     `Could not find linkedJobIdNum ${linkedJobIdNum} in current job page size of ${prevJobPageSize}. Doubling to ${
//     //       prevJobPageSize * 2
//     //     }.`
//     //   );
//     //   return prevJobPageSize * 2;
//     // });

//     const { jobs, isPreviousData: isJobPageLoading } = useListJobs({
//       configId: connection.connectionId,
//       configTypes: ["sync", "reset_connection"],
//       pagination: {
//         pageSize: jobPageSize,
//       },
//     });
//   }
// };
