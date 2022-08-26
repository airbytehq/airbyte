import FrequencyConfig from "config/FrequencyConfig.json";
import { ConnectionSchedule } from "core/request/AirbyteClient";
import { equal } from "utils/objects";

export const getFrequencyConfig = (schedule?: ConnectionSchedule) =>
  FrequencyConfig.find((item) => (!schedule && !item.config) || equal(item.config, schedule));
