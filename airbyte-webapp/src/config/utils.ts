import { ConnectionScheduleData } from "core/request/AirbyteClient";

export const getScheduleInfo = (scheduleData: ConnectionScheduleData) => {
  if (scheduleData.cron) {
    return `${scheduleData.cron.cronExpression} ${scheduleData.cron.cronTimeZone}`;
  } else if (scheduleData.basicSchedule) {
    return `${scheduleData.basicSchedule.units} ${scheduleData.basicSchedule.timeUnit}`;
  }
  // this will never get called since scheduleData will always have one of those two properties
  return null;
};
