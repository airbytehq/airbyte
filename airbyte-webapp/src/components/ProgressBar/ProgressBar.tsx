import { Line } from "rc-progress";

import { getJobStatus } from "components/JobItem/JobItem";

import { SynchronousJobRead } from "core/request/AirbyteClient";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/JobsList";

export var ProgressBar = ({ percent, job }: { percent?: number; job: JobsWithJobs | SynchronousJobRead }) => {
  if (!percent) {
    percent = Math.random() * 100;
  }
  const jobStatus = getJobStatus(job);

  console.log(job);

  // colors from `_colors.scss` TODO: Use the SCSS variables maybe?
  let color = "white";
  switch (jobStatus) {
    case "pending":
      color = "#cbc8ff";
      break;
    case "running":
      color = "#cbc8ff";
      break;
    case "incomplete":
      color = "#fdf8e1";
      break;
    case "failed":
      color = "#e64228";
      break;
    case "succeeded":
      color = "#67dae1";
      percent = 100; // just to be safe
      break;
    case "cancelled":
      percent = 0; // just to be safe
      break;
  }

  return <Line percent={percent} strokeColor={[color]} />;
};
