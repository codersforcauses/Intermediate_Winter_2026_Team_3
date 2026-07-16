export interface GameDetails {
  steam_appid: number;
  name: string;
  short_description: string;
  header_image: string;
  icon_url: string;
  developers: string;
  publishers: string;
  release_date: string | null;
  is_free: boolean;
  review_score: number | null;
  review_score_desc: string;
  total_reviews: number | null;
  genres: string[];
  categories: string[];
  last_synced: string | null;
}

export interface UserGame {
  game: GameDetails;
  playtime_forever_minutes: number;
  playtime_recent_minutes: number;
  playtime_windows_minutes: number;
  playtime_mac_minutes: number;
  playtime_linux_minutes: number;
  playtime_hours: number;
  last_played_at: string | null;
  last_synced: string | null;
}

export interface DashboardData {
  profile: {
    username: string;
    steamid: string;
    persona_name: string;
    avatar_url: string;
    country_code: string;
    last_synced: string | null;
  };
  summary: {
    friends: number;
    games_owned: number;
    achievements_unlocked: number;
    total_playtime_minutes: number;
    total_playtime_hours: number;
  };
  top_games: UserGame[];
}

export interface SessionData {
  authenticated: boolean;
  username?: string;
}
