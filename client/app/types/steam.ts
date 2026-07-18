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

export interface Achievement {
  api_name: string;
  display_name: string;
  description: string;
  icon_url: string;
  locked_icon_url: string;
  hidden: boolean;
  global_percent: number | null;
}

export interface PlayerAchievement {
  achievement: Achievement;
  achieved: boolean;
  unlocked_at: string | null;
  last_synced: string | null;
}

export interface SteamPlayer {
  steamid: string;
  persona_name: string;
  profile_url: string;
  avatar_url: string;
  avatar_full_url: string;
  country_code: string;
  time_created: string | null;
  last_synced: string | null;
}

export interface FriendRecord {
  friend: SteamPlayer;
  friends_since: string | null;
  unlocked_achievements: number;
}

export interface FriendAchievementSummary {
  friend: SteamPlayer;
  steam_appid: number;
  game_name: string;
  unlocked: number;
  total: number;
  achievements: PlayerAchievement[];
}

export interface NewsItem {
  external_id: string;
  steam_appid: number;
  game_name: string;
  title: string;
  url: string;
  author: string;
  published_at: string;
  contents: string;
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

export interface FriendProfileGame {
  steam_appid: number;
  name: string;
  header_image: string;
  icon_url: string;
  playtime_forever_minutes: number;
  playtime_recent_minutes: number;
  shared: boolean;
}

export interface FriendProfile {
  friend: SteamPlayer;
  status: string;
  real_name: string;
  current_game: string;
  current_game_appid: number | null;
  last_logoff: string | null;
  games_private: boolean;
  summary: {
    games_owned: number;
    shared_games: number;
    achievements_unlocked: number;
    total_playtime_minutes: number;
    total_playtime_hours: number;
  };
  recent_games: FriendProfileGame[];
  top_games: FriendProfileGame[];
}


export interface AchievementGameSummary {
  achievement__game__steam_appid: number;
  achievement__game__name: string;
  achievement__game__header_image: string;
  total: number;
  unlocked: number;
  completion_percent: number;
}

export interface AchievementSummary {
  total: number;
  unlocked: number;
  locked: number;
  completion_percent: number;
  games: AchievementGameSummary[];
}
