import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import AgentPage from "./pages/AgentPage";
import AgentRunsPage from "./pages/AgentRunsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ThreadWorkspacePage from "./pages/ThreadWorkspacePage";
import InboxPage from "./pages/InboxPage"; // NEW

function App() {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                {/* Make Inbox the new home page */}
                <Route path="/" element={<InboxPage />} />
                <Route path="/agent" element={<AgentPage />} />
                <Route path="/runs" element={<AgentRunsPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/thread-demo" element={<ThreadWorkspacePage />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;