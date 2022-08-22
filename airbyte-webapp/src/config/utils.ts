import { ConnectionSchedule } from "core/request/AirbyteClient";

export const getFrequencyType = (schedule?: ConnectionSchedule) =>
  schedule ? `${schedule.units} ${schedule.timeUnit}` : "manual";
