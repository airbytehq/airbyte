export interface FormChangeTrackerServiceApi {
  hasFormChanges: boolean;
  trackFormChange: (id: string, changed: boolean) => void;
  clearFormChange: (id: string) => void;
  clearAllFormChanges: () => void;
}
