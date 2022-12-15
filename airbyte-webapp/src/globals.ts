// This file should contain all stateful modification that need to be made to libraries.
// In general this is a bad pattern that should try to be avoided, but some libraries will
// require plugins to be registered to their global instance. This file encapsulates all those
// stateful modifications.

import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import utc from "dayjs/plugin/utc";

// Configure dayjs instance
dayjs.extend(customParseFormat);
dayjs.extend(utc);
