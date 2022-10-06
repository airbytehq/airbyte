import { ConnectionScheduleData } from "core/request/AirbyteClient";

export const getFrequencyFromScheduleData = (scheduleData?: ConnectionScheduleData) => {
  if (!scheduleData) {
    return "manual";
  } else if (scheduleData.cron) {
    return `${scheduleData.cron.cronExpression} ${scheduleData.cron.cronTimeZone}`;
  } else if (scheduleData.basicSchedule) {
    return `${scheduleData.basicSchedule.units} ${scheduleData.basicSchedule.timeUnit}`;
  }
  // this should never get called but the linter wants a catch-all
  return null;
};
