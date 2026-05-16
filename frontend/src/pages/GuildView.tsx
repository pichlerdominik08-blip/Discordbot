import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, Entry, GuildStats } from "../lib/api";
import { Shield, Info, ArrowLeft, Clock, AlertTriangle, CheckCircle, MessageSquare, Activity } from "lucide-react";

export default function GuildView() {
  const { guildId } = useParams<{ guildId: string }>();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [stats, setStats] = useState<GuildStats | null>(null);
  const [filter, setFilter] = useState<"all" | "violation" | "info">("all");
  const [statusFilter, setStatusFilter] = useState<"all" | "open" | "closed">("all");
  const [loading, setLoading] = useState(true);
  const [guildName, setGuildName] = useState("");

  useEffect(() => {
    if (!guildId) return;
    async function load() {
      try {
        const [entriesData, statsData, guildData] = await Promise.all([
          api.getEntries({ guild_id: guildId }),
          api.getGuildStats(guildId!),
          api.getGuild(guildId!),
        ]);
        setEntries(entriesData);
        setStats(statsData);
        setGuildName(guildData.guild_name);
      } catch (err) {
        console.error("Failed to load:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [guildId]);

  const filtered = entries.filter((e) => {
    if (filter !== "all" && e.entry_type !== filter) return false;
    if (statusFilter === "open" && !e.is_open) return false;
    if (statusFilter === "closed" && e.is_open) return false;
    return true;
  });

  const severityColor: Record<string, string> = {
    leicht: "text-green-400 bg-green-400/10 border-green-400/20",
    mittel: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    schwer: "text-red-400 bg-red-400/10 border-red-400/20",
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Zurueck
        </Link>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">{guildName}</h1>
          <p className="text-gray-400 mt-1">Server ID: {guildId}</p>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
              <div className="flex items-center gap-2 text-red-400 mb-1">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm font-medium">Verstoesse</span>
              </div>
              <p className="text-2xl font-bold text-white">{stats.violations}</p>
            </div>
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
              <div className="flex items-center gap-2 text-blue-400 mb-1">
                <Info className="h-4 w-4" />
                <span className="text-sm font-medium">Infos</span>
              </div>
              <p className="text-2xl font-bold text-white">{stats.infos}</p>
            </div>
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
              <div className="flex items-center gap-2 text-green-400 mb-1">
                <Activity className="h-4 w-4" />
                <span className="text-sm font-medium">Offen</span>
              </div>
              <p className="text-2xl font-bold text-white">{stats.open}</p>
            </div>
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
              <div className="flex items-center gap-2 text-purple-400 mb-1">
                <MessageSquare className="h-4 w-4" />
                <span className="text-sm font-medium">Nachrichten</span>
              </div>
              <p className="text-2xl font-bold text-white">{stats.total_messages}</p>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-3 mb-6">
          <div className="flex rounded-lg border border-gray-700 overflow-hidden">
            {(["all", "violation", "info"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  filter === f
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                {f === "all" ? "Alle" : f === "violation" ? "Verstoesse" : "Infos"}
              </button>
            ))}
          </div>
          <div className="flex rounded-lg border border-gray-700 overflow-hidden">
            {(["all", "open", "closed"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  statusFilter === s
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:text-white"
                }`}
              >
                {s === "all" ? "Alle" : s === "open" ? "Offen" : "Geschlossen"}
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12">
            <Shield className="mx-auto h-12 w-12 text-gray-600 mb-3" />
            <p className="text-gray-500">Keine Eintraege gefunden</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((entry) => (
              <Link
                key={entry.id}
                to={`/entry/${entry.id}`}
                className="block rounded-xl border border-gray-700 bg-gray-800/50 p-5 hover:border-blue-500/50 hover:bg-gray-800 transition-all duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {entry.entry_type === "violation" ? (
                      <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5" />
                    ) : (
                      <Info className="h-5 w-5 text-blue-400 mt-0.5" />
                    )}
                    <div>
                      <h3 className="text-lg font-semibold text-white">{entry.name}</h3>
                      <p className="text-gray-400 text-sm mt-1 line-clamp-2">{entry.description}</p>
                      <div className="flex items-center gap-3 mt-3">
                        {entry.severity && (
                          <span className={`text-xs px-2 py-1 rounded-full border ${severityColor[entry.severity] || "text-gray-400"}`}>
                            {entry.severity.charAt(0).toUpperCase() + entry.severity.slice(1)}
                          </span>
                        )}
                        {entry.author_name && (
                          <span className="text-xs text-gray-500">
                            von {entry.author_name}
                          </span>
                        )}
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(entry.created_at).toLocaleDateString("de-DE", {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {entry.is_open ? (
                      <span className="flex items-center gap-1 text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-full">
                        <Activity className="h-3 w-3" />
                        Offen
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-gray-400 bg-gray-400/10 px-2 py-1 rounded-full">
                        <CheckCircle className="h-3 w-3" />
                        Geschlossen
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
