import { ConnectionScheduleDataBasicSchedule } from "core/request/AirbyteClient";

export const frequencyConfig: Array<ConnectionScheduleDataBasicSchedule | null> = [
  null, // manual
  {
    units: 1,
    timeUnit: "hours",
  },
  {
    units: 2,
    timeUnit: "hours",
  },
  {
    units: 3,
    timeUnit: "hours",
  },
  {
    units: 6,
    timeUnit: "hours",
  },
  {
    units: 8,
    timeUnit: "hours",
  },
  {
    units: 12,
    timeUnit: "hours",
  },
  {
    units: 24,
    timeUnit: "hours",
  },
];
