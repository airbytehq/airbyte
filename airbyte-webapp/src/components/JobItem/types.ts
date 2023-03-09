import { JobWithAttemptsRead } from "core/request/AirbyteClient";

export interface JobsWithJobs extends JobWithAttemptsRead {
  job: Exclude<JobWithAttemptsRead["job"], undefined>;
}
