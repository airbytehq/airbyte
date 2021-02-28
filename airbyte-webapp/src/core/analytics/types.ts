interface SegmentAnalytics {
  page: (name?: string) => void;
  reset: () => void;
  alias: (newId: string) => void;
  track: (name: string, properties: Record<string, unknown>) => void;
  identify: (traits: Record<string, unknown>, userId?: string) => void;
  group: (organisationId: string, traits: Record<string, unknown>) => void;
}

export type { SegmentAnalytics };
