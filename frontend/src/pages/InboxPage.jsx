import { useEffect, useState, useMemo } from "react";
import { getInbox, stopStream, bulkArchive, bulkMarkSpam, bulkAssign } from "../api/agentApi";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function InboxPage() {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState("All");
    const [searchQuery, setSearchQuery] = useState("");
    const [sortConfig, setSortConfig] = useState({ key: "timestamp", direction: "desc" });
    const [selectedIds, setSelectedIds] = useState([]);
    const [groupByThread, setGroupByThread] = useState(false);
    
    // Streaming state
    const [streamSpeed, setStreamSpeed] = useState(1);
    const [isStreaming, setIsStreaming] = useState(false);
    const [streamProgress, setStreamProgress] = useState(null);
    const [streamError, setStreamError] = useState(null);

    const fetchInbox = async () => {
        try {
            const data = await getInbox();
            setEmails(Array.isArray(data) ? data : []);
            setError(null);
        } catch (err) {
            console.error(err);
            setError("Failed to load inbox.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInbox();
        const interval = setInterval(fetchInbox, 10000);
        return () => clearInterval(interval);
    }, []);

    const tabs = ["All", "Needs Human", "Auto-Replied", "Escalated", "Spam"];

    const filteredEmails = useMemo(() => {
        let result = emails.filter((e) => {
            if (activeTab === "All") return true;
            if (activeTab === "Needs Human") return e.requires_human === true;
            if (activeTab === "Auto-Replied") return e.status === "Replied";
            if (activeTab === "Escalated") return e.status === "Escalated";
            if (activeTab === "Spam") return e.category === "Spam";
            return true;
        });

        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            result = result.filter((e) => {
                const subject = (e.subject || "").toLowerCase();
                const body = (e.body || "").toLowerCase();
                return subject.includes(query) || body.includes(query);
            });
        }

        if (sortConfig.key) {
            result = [...result].sort((a, b) => {
                const aVal = a[sortConfig.key];
                const bVal = b[sortConfig.key];
                if (aVal === bVal) return 0;
                if (aVal == null) return 1;
                if (bVal == null) return -1;
                const comparison = aVal < bVal ? -1 : 1;
                return sortConfig.direction === "asc" ? comparison : -comparison;
            });
        }

        return result;
    }, [emails, activeTab, searchQuery, sortConfig]);

    const groupedEmails = useMemo(() => {
        if (!groupByThread) return { "All Emails": filteredEmails };
        const groups = {};
        filteredEmails.forEach((email) => {
            const threadId = email.thread_id || "No Thread";
            if (!groups[threadId]) groups[threadId] = [];
            groups[threadId].push(email);
        });
        return groups;
    }, [filteredEmails, groupByThread]);

    const handleSort = (key) => {
        setSortConfig((prev) => ({
            key,
            direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc"
        }));
    };

    const toggleSelect = (id) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    };

    const toggleSelectAll = () => {
        if (selectedIds.length === filteredEmails.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(filteredEmails.map((e) => e.id));
        }
    };

    const handleBulkAction = async (action) => {
        if (selectedIds.length === 0) return;
        
        try {
            if (action === "archive") {
                await bulkArchive(selectedIds, "user");
            } else if (action === "spam") {
                await bulkMarkSpam(selectedIds, "user");
            } else if (action === "assign") {
                await bulkAssign(selectedIds, "user");
            }
            // Refresh inbox to show updated status
            fetchInbox();
        } catch (err) {
            console.error(err);
        } finally {
            setSelectedIds([]);
        }
    };

    const handleStartStream = async () => {
        try {
            setStreamError(null);
            setIsStreaming(true);
            setStreamProgress({ current: 0, total: 0 });
            
            const response = await fetch(`${API_BASE}/api/stream/start?speed=${streamSpeed}`, {
                method: "POST",
                headers: {
                    "Accept": "text/plain",
                    "Content-Type": "application/json"
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split("\n\n");
                
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === "progress") {
                            setStreamProgress(data);
                            // Refresh inbox to show new emails
                            fetchInbox();
                        } else if (data.type === "complete") {
                            setIsStreaming(false);
                            setStreamProgress(null);
                        }
                    }
                }
            }
        } catch (err) {
            console.error(err);
            setStreamError(`Failed to start stream: ${err.message}`);
            setIsStreaming(false);
        }
    };

    const handleStopStream = async () => {
        try {
            await stopStream();
            setIsStreaming(false);
            setStreamProgress(null);
        } catch (err) {
            console.error(err);
        }
    };

    const SortIcon = ({ columnKey }) => {
        if (sortConfig.key !== columnKey) return <span style={{ opacity: 0.4 }}>⇅</span>;
        return <span>{sortConfig.direction === "asc" ? "↑" : "↓"}</span>;
    };

    return (
        <div className="container">
            <h1>Mission Control Inbox</h1>
            <p className="muted">Live monitoring of inbound emails and triage status.</p>

            {/* Streaming Controls */}
            <div className="card" style={{ marginBottom: "16px", padding: "12px" }}>
                <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <label className="label" style={{ margin: 0 }}>Stream Speed:</label>
                        <input
                            type="range"
                            min="1"
                            max="100"
                            value={streamSpeed}
                            onChange={(e) => setStreamSpeed(Number(e.target.value))}
                            disabled={isStreaming}
                            style={{ width: "120px" }}
                        />
                        <span className="muted" style={{ fontSize: "12px", minWidth: "60px" }}>
                            {streamSpeed} email/sec
                        </span>
                    </div>
                    {!isStreaming ? (
                        <button onClick={handleStartStream} disabled={isStreaming}>
                            Start Stream
                        </button>
                    ) : (
                        <button className="secondary" onClick={handleStopStream}>
                            Stop Stream
                        </button>
                    )}
                    {streamProgress && (
                        <span className="muted" style={{ fontSize: "12px" }}>
                            {streamProgress.current} / {streamProgress.total} emails processed
                        </span>
                    )}
                    {streamError && (
                        <span className="error-text" style={{ fontSize: "12px" }}>
                            {streamError}
                        </span>
                    )}
                </div>
            </div>

            <div style={{ display: "flex", gap: "8px", marginBottom: "16px", flexWrap: "wrap", alignItems: "center" }}>
                {tabs.map(tab => (
                    <button
                        key={tab}
                        className={activeTab === tab ? "" : "secondary"}
                        onClick={() => setActiveTab(tab)}
                    >
                        {tab}
                    </button>
                ))}
                <input
                    type="text"
                    placeholder="Search subject or body..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{ padding: "8px 10px", border: "1px solid var(--border)", borderRadius: "6px", minWidth: "220px" }}
                />
                <button
                    className={groupByThread ? "" : "secondary"}
                    onClick={() => setGroupByThread(!groupByThread)}
                >
                    {groupByThread ? "Ungroup" : "Group by Thread"}
                </button>
                {selectedIds.length > 0 && (
                    <>
                        <span className="muted" style={{ marginLeft: "8px" }}>{selectedIds.length} selected</span>
                        <button className="secondary" onClick={() => handleBulkAction("archive")}>Archive</button>
                        <button className="secondary" onClick={() => handleBulkAction("spam")}>Mark as Spam</button>
                        <button className="secondary" onClick={() => handleBulkAction("assign")}>Assign</button>
                    </>
                )}
            </div>

            {loading && emails.length === 0 ? (
                <p className="muted">Loading inbox...</p>
            ) : error ? (
                <p className="error-text">{error}</p>
            ) : filteredEmails.length === 0 ? (
                <div className="empty-state">No emails found for this filter.</div>
            ) : (
                Object.entries(groupedEmails).map(([group, groupEmails]) => (
                    <div key={group} style={{ marginBottom: "24px" }}>
                        {groupByThread && (
                            <h3 style={{ marginBottom: "8px" }}>{group}</h3>
                        )}
                        <table>
                            <thead>
                                <tr>
                                    <th>
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.length === filteredEmails.length && filteredEmails.length > 0}
                                            onChange={toggleSelectAll}
                                        />
                                    </th>
                                    <th onClick={() => handleSort("status")}>Status <SortIcon columnKey="status" /></th>
                                    <th onClick={() => handleSort("sender")}>Sender <SortIcon columnKey="sender" /></th>
                                    <th onClick={() => handleSort("subject")}>Subject <SortIcon columnKey="subject" /></th>
                                    <th onClick={() => handleSort("category")}>Category <SortIcon columnKey="category" /></th>
                                    <th onClick={() => handleSort("urgency")}>Urgency <SortIcon columnKey="urgency" /></th>
                                    <th onClick={() => handleSort("sentiment")}>Sentiment <SortIcon columnKey="sentiment" /></th>
                                    <th onClick={() => handleSort("timestamp")}>Timestamp <SortIcon columnKey="timestamp" /></th>
                                </tr>
                            </thead>
                            <tbody>
                                {groupEmails.map((email) => (
                                    <tr key={email.id} className="clickable">
                                        <td>
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(email.id)}
                                                onChange={() => toggleSelect(email.id)}
                                            />
                                        </td>
                                        <td><strong>{email.status}</strong></td>
                                        <td>{email.sender}</td>
                                        <td>{email.subject}</td>
                                        <td>
                                            {email.category && <span className="badge">{email.category}</span>}
                                        </td>
                                        <td>
                                            {email.urgency && (
                                                <span className={`badge urgency-${email.urgency.toLowerCase()}`}>
                                                    {email.urgency}
                                                </span>
                                            )}
                                        </td>
                                        <td>
                                            {email.sentiment && (
                                                <span className={`badge sentiment-${email.sentiment.toLowerCase()}`}>
                                                    {email.sentiment}
                                                </span>
                                            )}
                                        </td>
                                        <td>{new Date(email.timestamp).toLocaleString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ))
            )}
        </div>
    );
}

export default InboxPage;
