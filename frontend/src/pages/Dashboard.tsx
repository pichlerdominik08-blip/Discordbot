import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Guild, GuildStats } from "../lib/api";
import { Shield, Info, MessageSquare, Activity } from "lucide-react";

interface GuildWithStats extends Guild {
  stats?: GuildStats;
}

export default function Dashboard() {
  const [guilds, setGuilds] = useState<GuildWithStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getGuilds();
        const withStats = await Promise.all(
          data.map(async (g) => {
            try {
              const stats = await api.getGuildStats(g.guild_id);
              return { ...g, stats };
            } catch {
              return g;
            }
          })
        );
        setGuilds(withStats);
      } catch (err) {
        console.error("Failed to load guilds:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (guilds.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Shield className="mx-auto h-16 w-16 text-gray-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-300 mb-2">Keine Server gefunden</h2>
          <p className="text-gray-500">
            Richte den Bot zuerst auf deinem Discord Server ein.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-500" />
            Discord Panel
          </h1>
          <p className="text-gray-400 mt-2">
            Uebersicht aller Server
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {guilds.map((guild) => (
            <Link
              key={guild.guild_id}
              to={`/guild/${guild.guild_id}`}
              className="block rounded-xl border border-gray-700 bg-gray-800/50 p-6 hover:border-blue-500/50 hover:bg-gray-800 transition-all duration-200"
            >
              <h3 className="text-xl font-semibold text-white mb-4">
                {guild.guild_name}
              </h3>

              {guild.stats && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Shield className="h-4 w-4 text-red-400" />
                    <span className="text-gray-400">Verstoesse:</span>
                    <span className="text-white font-medium">{guild.stats.violations}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Info className="h-4 w-4 text-blue-400" />
                    <span className="text-gray-400">Infos:</span>
                    <span className="text-white font-medium">{guild.stats.infos}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Activity className="h-4 w-4 text-green-400" />
                    <span className="text-gray-400">Offen:</span>
                    <span className="text-white font-medium">{guild.stats.open}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <MessageSquare className="h-4 w-4 text-purple-400" />
                    <span className="text-gray-400">Nachrichten:</span>
                    <span className="text-white font-medium">{guild.stats.total_messages}</span>
                  </div>
                </div>
              )}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
