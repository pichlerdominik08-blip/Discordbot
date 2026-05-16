import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, Entry, Message } from "../lib/api";
import { ArrowLeft, AlertTriangle, Info, Clock, User, MessageSquare, CheckCircle, Activity } from "lucide-react";

export default function EntryDetail() {
  const { entryId } = useParams<{ entryId: string }>();
  const [entry, setEntry] = useState<Entry | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!entryId) return;
    async function load() {
      try {
        const id = parseInt(entryId!, 10);
        const [entryData, messagesData] = await Promise.all([
          api.getEntry(id),
          api.getTranscript(id),
        ]);
        setEntry(entryData);
        setMessages(messagesData);
      } catch (err) {
        console.error("Failed to load entry:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [entryId]);

  const severityConfig: Record<string, { color: string; label: string }> = {
    leicht: { color: "text-green-400 bg-green-400/10 border-green-400/30", label: "Leicht" },
    mittel: { color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30", label: "Mittel" },
    schwer: { color: "text-red-400 bg-red-400/10 border-red-400/30", label: "Schwer" },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Eintrag nicht gefunden</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto">
        <Link
          to={`/guild/${entry.guild_id}`}
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Zurueck zum Server
        </Link>

        {/* Entry Header */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="rounded-full p-3 bg-gray-700/50">
              {entry.entry_type === "violation" ? (
                <AlertTriangle className="h-6 w-6 text-red-400" />
              ) : (
                <Info className="h-6 w-6 text-blue-400" />
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-white">{entry.name}</h1>
                {entry.is_open ? (
                  <span className="flex items-center gap-1 text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-full border border-green-400/20">
                    <Activity className="h-3 w-3" />
                    Offen
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-gray-400 bg-gray-400/10 px-2 py-1 rounded-full border border-gray-400/20">
                    <CheckCircle className="h-3 w-3" />
                    Geschlossen
                  </span>
                )}
              </div>

              <p className="text-gray-300 mb-4">{entry.description}</p>

              <div className="flex flex-wrap items-center gap-4 text-sm">
                <span className={`px-3 py-1 rounded-full border text-xs font-medium ${
                  entry.entry_type === "violation"
                    ? "text-red-400 bg-red-400/10 border-red-400/20"
                    : "text-blue-400 bg-blue-400/10 border-blue-400/20"
                }`}>
                  {entry.entry_type === "violation" ? "Verstoss" : "Information"}
                </span>

                {entry.severity && severityConfig[entry.severity] && (
                  <span className={`px-3 py-1 rounded-full border text-xs font-medium ${severityConfig[entry.severity].color}`}>
                    {severityConfig[entry.severity].label}
                  </span>
                )}

                {entry.author_name && (
                  <span className="flex items-center gap-1 text-gray-400">
                    <User className="h-3.5 w-3.5" />
                    {entry.author_name}
                  </span>
                )}

                <span className="flex items-center gap-1 text-gray-500">
                  <Clock className="h-3.5 w-3.5" />
                  {new Date(entry.created_at).toLocaleDateString("de-DE", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>

                {entry.closed_at && (
                  <span className="flex items-center gap-1 text-gray-500">
                    <CheckCircle className="h-3.5 w-3.5" />
                    Geschlossen: {new Date(entry.closed_at).toLocaleDateString("de-DE", {
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                )}
              </div>

              {entry.channel_name && (
                <p className="text-xs text-gray-500 mt-3">
                  Kanal: #{entry.channel_name}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Transcript */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50">
          <div className="border-b border-gray-700 px-6 py-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-blue-400" />
              Transcript
              <span className="text-sm font-normal text-gray-500">
                ({messages.length} {messages.length === 1 ? "Nachricht" : "Nachrichten"})
              </span>
            </h2>
          </div>

          {messages.length === 0 ? (
            <div className="p-8 text-center">
              <MessageSquare className="mx-auto h-10 w-10 text-gray-600 mb-3" />
              <p className="text-gray-500">Keine Nachrichten vorhanden</p>
              <p className="text-gray-600 text-sm mt-1">
                {entry.is_open
                  ? "Nachrichten werden live gespeichert sobald sie geschrieben werden."
                  : "Fuer diesen Eintrag wurden keine Nachrichten gespeichert."}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-700/50">
              {messages.map((msg) => (
                <div key={msg.id} className="px-6 py-4 hover:bg-gray-700/20 transition-colors">
                  <div className="flex items-start gap-3">
                    {msg.author_avatar ? (
                      <img
                        src={msg.author_avatar}
                        alt=""
                        className="h-8 w-8 rounded-full flex-shrink-0"
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                        <User className="h-4 w-4 text-gray-400" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-blue-400">
                          {msg.author_name || "Unbekannt"}
                        </span>
                        {msg.created_at && (
                          <span className="text-xs text-gray-600">
                            {new Date(msg.created_at).toLocaleDateString("de-DE", {
                              day: "2-digit",
                              month: "2-digit",
                              year: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                              second: "2-digit",
                            })}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-300 text-sm whitespace-pre-wrap break-words">
                        {msg.content || "(kein Inhalt)"}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
