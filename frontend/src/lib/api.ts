import type { ComparisonResult, Match, Player, TeamContext } from "./api-types";

const BASE =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchJustFinished(limit = 8): Promise<Match[]> {
  return getJson(`/v1/chelsea/just-finished?limit=${limit}`);
}

export function fetchContext(): Promise<TeamContext | null> {
  return getJson("/v1/chelsea/context");
}

export function searchPlayers(q: string): Promise<Player[]> {
  return getJson(`/v1/players/search?q=${encodeURIComponent(q)}`);
}

export function fetchComparison(
  playerIds: string[],
  seasonFrom?: string,
  seasonTo?: string,
): Promise<ComparisonResult> {
  const params = new URLSearchParams({ player_ids: playerIds.join(",") });
  if (seasonFrom) params.set("season_from", seasonFrom);
  if (seasonTo) params.set("season_to", seasonTo);
  return getJson(`/v1/compare?${params.toString()}`);
}
