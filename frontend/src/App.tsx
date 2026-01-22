import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Settings from "./pages/Settings";
import Tickets from "./pages/Tickets";
import TicketDetail from "./pages/TicketDetail";
import Members from "./pages/Members";
import Invites from "./pages/Invites";
import Commands from "./pages/Commands";
import Databases from "./pages/Databases";
import DatabaseTable from "./pages/DatabaseTable";
import Services from "./pages/Services";
import GuildStats from "./pages/GuildStats";
import About from "./pages/About";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="settings" element={<Settings />} />
            <Route path="tickets" element={<Tickets />} />
            <Route path="tickets/:ticketId" element={<TicketDetail />} />
            <Route path="members" element={<Members />} />
            <Route path="invites" element={<Invites />} />
            <Route path="commands" element={<Commands />} />
            <Route path="databases" element={<Databases />} />
            <Route
              path="databases/table/:tableName"
              element={<DatabaseTable />}
            />
            <Route path="services" element={<Services />} />
            <Route path="guild-stats" element={<GuildStats />} />
            <Route path="about" element={<About />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
