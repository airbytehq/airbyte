export interface FormChangeTrackerServiceApi {
  clearFormChange: (id: string) => void;
  trackFormChange: (id: string, changed: boolean) => void;
}
