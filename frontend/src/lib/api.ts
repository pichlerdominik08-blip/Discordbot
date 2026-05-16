const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Guild {
  guild_id: string;
  guild_name: string;
  panel_channel: string | null;
  panel_message: string | null;
  info_category: string | null;
  role_id: string | null;
  logs_enabled: number;
  log_channel: string | null;
}

export interface Entry {
  id: number;
  guild_id: string;
  entry_type: "violation" | "info";
  name: string;
  description: string;
  severity: string | null;
  author_name: string | null;
  author_id: string | null;
  author_avatar: string | null;
  channel_id: string | null;
  channel_name: string | null;
  category_id: string | null;
  is_open: number;
  created_at: string;
  closed_at: string | null;
}

export interface Message {
  id: number;
  entry_id: number;
  guild_id: string;
  channel_id: string;
  message_id: string;
  author_name: string | null;
  author_id: string | null;
  author_avatar: string | null;
  content: string | null;
  created_at: string | null;
}

export interface GuildStats {
  violations: number;
  infos: number;
  open: number;
  total_messages: number;
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getGuilds: () => apiFetch<Guild[]>("/api/guilds"),
  getGuild: (id: string) => apiFetch<Guild>(`/api/guilds/${id}`),
  getGuildStats: (id: string) => apiFetch<GuildStats>(`/api/guilds/${id}/stats`),
  getEntries: (params?: { guild_id?: string; entry_type?: string; is_open?: number }) => {
    const search = new URLSearchParams();
    if (params?.guild_id) search.set("guild_id", params.guild_id);
    if (params?.entry_type) search.set("entry_type", params.entry_type);
    if (params?.is_open !== undefined) search.set("is_open", String(params.is_open));
    return apiFetch<Entry[]>(`/api/entries?${search.toString()}`);
  },
  getEntry: (id: number) => apiFetch<Entry>(`/api/entries/${id}`),
  getTranscript: (entryId: number) => apiFetch<Message[]>(`/api/entries/${entryId}/messages`),
};
