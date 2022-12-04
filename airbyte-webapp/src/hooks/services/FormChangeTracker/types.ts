export interface FormChangeTrackerServiceApi {
  trackFormChange: (id: string, changed: boolean) => void;
  clearFormChange: (id: string) => void;
  clearAllFormChanges: () => void;
}
