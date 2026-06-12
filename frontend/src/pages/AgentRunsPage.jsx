import { useEffect, useState } from "react";
import { getAgentRuns } from "../api/agentApi";
import ReasoningTrace from "../components/ReasoningTrace";

function AgentRunsPage() {
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedId, setExpandedId] = useState(null);

    const fetchRuns = async () => {
        try {
            setLoading(true);
            const data = await getAgentRuns();
            setRuns(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error(err);
            setError("Failed to load agent runs.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRuns();
    }, []);

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    return (
        <div className="container">
            <h1>Agent Runs</h1>
            <p className="muted">
                History of every agent execution, including final action taken and
                full reasoning trace.
            </p>

            {loading ? (
                <p className="muted">Loading…</p>
            ) : error ? (
                <p className="error-text">{error}</p>
            ) : runs.length === 0 ? (
                <div className="empty-state">No agent runs yet. Run the agent from the Agent page.</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email ID</th>
                            <th>Status</th>
                            <th>Final Action</th>
                            <th>Created At</th>
                        </tr>
                    </thead>

                    <tbody>
                        {runs.map((run) => (
                            <>
                                <tr key={run.id} className="clickable" onClick={() => toggleExpand(run.id)}>
                                    <td>{run.id}</td>
                                    <td>{run.email_id}</td>
                                    <td><span className="badge">{run.status}</span></td>
                                    <td><code>{run.final_action}</code></td>
                                    <td>{run.created_at}</td>
                                </tr>

                                {expandedId === run.id && (
                                    <tr key={`${run.id}-trace`}>
                                        <td colSpan={5} style={{ background: "var(--code-bg)" }}>
                                            <ReasoningTrace trace={run.reasoning_trace} />
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default AgentRunsPage;
