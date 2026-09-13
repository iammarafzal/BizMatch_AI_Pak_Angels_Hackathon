/**
 * BizMatch AI - Core TypeScript Schema Contracts
 * Re-exports strict types from @/types/api for unified typing across the application.
 */

export * from "@/types/api";

import {
  CandidateMatchSummary,
  FactorScores as FactorScoresBase,
} from "@/types/api";

export type MatchResult = CandidateMatchSummary;
export type MatchRecord = CandidateMatchSummary;

export type FactorScores = FactorScoresBase;
