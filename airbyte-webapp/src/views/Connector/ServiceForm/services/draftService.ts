import { useRef } from "react";

const STORAGE_KEY = "connector_drafts";

class DraftService {
  private drafts: Record<string, unknown>;

  constructor() {
    try {
      this.drafts = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}");
    } catch {
      this.drafts = {};
    }
  }

  public saveDraft(serviceKey: string, config: unknown): void {
    this.drafts[serviceKey] = config;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this.drafts));
  }

  public getDraft(serviceKey: string): unknown | undefined {
    return this.drafts[serviceKey];
  }

  public listAvailableDrafts(): string[] {
    return Object.keys(this.drafts);
  }

  public clearDrafts(): void {
    this.drafts = {};
    localStorage.removeItem(STORAGE_KEY);
  }
}

export const useDraftService = () => {
  const service = useRef<DraftService>();
  if (!service.current) {
    service.current = new DraftService();
  }
  return service.current;
};
