import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

export const mockStreamConfiguration: AirbyteStreamConfiguration = {
  fieldSelectionEnabled: false,
  selectedFields: [],
  selected: true,
  syncMode: "full_refresh",
  destinationSyncMode: "overwrite",
};
