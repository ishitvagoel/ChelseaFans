export type AppMeta = {
  demo: boolean;
  message: string;
  provider_notes?: string[];
};

export type Confidence = {
  source: string;
  score: number;
  coverage_notes: string;
};

export type Club = {
  name: string;
  short_name: string | null;
  crest_url: string | null;
};

export type Score = {
  home: number;
  away: number;
};

export type EventType = "GOAL" | "ASSIST" | "CARD" | "SUBSTITUTION" | "OTHER";

export type MatchEvent = {
  minute: number | null;
  event_type: EventType;
  player_name: string | null;
  detail: string | null;
};

export type Player = {
  id: string;
  name: string;
  position: string | null;
  nationality: string | null;
  shirt_number: number | null;
};

export type PlayerMatchStats = {
  player: Player;
  minutes: number | null;
  goals: number | null;
  assists: number | null;
  rating: number | null;
  shots: number | null;
  key_passes: number | null;
  progressive_passes: number | null;
  progressive_carries: number | null;
  tackles: number | null;
  source: string;
};

export type Match = {
  id: string;
  utc_kickoff: string;
  competition: string;
  home: Club;
  away: Club;
  score: Score | null;
  status: string;
  events: MatchEvent[];
  player_stats: PlayerMatchStats[];
  venue: string | null;
  matchday: number | null;
  sources: Confidence[];
};

export type TeamContext = {
  team_name: string;
  competition: string;
  position: number | null;
  played: number | null;
  points: number | null;
  form: string | null;
  goal_difference: number | null;
  sources: Confidence[];
};

export type MetricSlice = {
  label: string;
  goals: number | null;
  assists: number | null;
  minutes: number | null;
  rating: number | null;
  progressive_passes: number | null;
  progressive_carries: number | null;
};

export type PlayerComparison = {
  player: Player;
  season: MetricSlice;
  career: MetricSlice;
  source_notes: string[];
};

export type ComparisonResult = {
  players: PlayerComparison[];
  season_from: string | null;
  season_to: string | null;
  sources: Confidence[];
};
