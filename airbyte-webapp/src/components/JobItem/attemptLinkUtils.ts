import { useLocation } from "react-router-dom";

import { AttemptRead } from "core/request/AirbyteClient";

const PARSE_REGEXP = /^#(?<jobId>\w*)::(?<attemptId>\w*)$/;

/**
 * Create and returns a link for a specific job and (optionally) attempt.
 * The returned string is the hash part of a URL.
 */
export const buildAttemptLink = (jobId: number | string, attemptId?: AttemptRead["id"]): string => {
  return `#${jobId}::${attemptId ?? ""}`;
};

/**
 * Parses a hash part of the URL into a jobId and attemptId.
 * This is the reverse function of {@link buildAttemptLink}.
 */
export const parseAttemptLink = (link: string): { jobId?: string; attemptId?: string } => {
  const match = link.match(PARSE_REGEXP);
  if (!match) {
    return {};
  }
  return {
    jobId: match.groups?.jobId,
    attemptId: match.groups?.attemptId,
  };
};

/**
 * Returns the information about which attempt was linked to from the hash if available.
 */
export const useAttemptLink = () => {
  const { hash } = useLocation();
  return parseAttemptLink(hash);
};
