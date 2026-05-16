import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import GuildView from "./pages/GuildView";
import EntryDetail from "./pages/EntryDetail";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/guild/:guildId" element={<GuildView />} />
        <Route path="/entry/:entryId" element={<EntryDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
