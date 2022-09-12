import { ConnectionScheduleDataBasicSchedule } from "core/request/AirbyteClient";

export const getFrequencyType = (schedule?: ConnectionScheduleDataBasicSchedule) =>
  schedule ? `${schedule.units} ${schedule.timeUnit}` : "manual";
