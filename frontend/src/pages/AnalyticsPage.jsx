import { useEffect, useState, useMemo } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    LineChart,
    Line,
    CartesianGrid
} from "recharts";
import {
    getAgentRuns,
    getSentimentTrend,
    getCategoryBreakdown,
    getDashboardStats,
    getAtRiskAccounts
} from "../api/agentApi";

function AnalyticsPage() {
    const [actionData, setActionData] = useState([]);
    const [categoryData, setCategoryData] = useState([]);
    const [sentimentData, setSentimentData] = useState([]);
    const [atRiskAccounts, setAtRiskAccounts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const [runs, categoryBreakdown, sentimentTrend, dashboardStats, atRisk] = await Promise.all([
                    getAgentRuns(),
                    getCategoryBreakdown(),
                    getSentimentTrend("all"),
                    getDashboardStats(),
                    getAtRiskAccounts()
                ]);

                const counts = {};
                (Array.isArray(runs) ? runs : []).forEach((run) => {
                    const action = run.final_action || "none";
                    counts[action] = (counts[action] || 0) + 1;
                });
                setActionData(
                    Object.entries(counts).map(([action, count]) => ({ action, count }))
                );

                setCategoryData(
                    Object.entries(categoryBreakdown || {}).map(([category, count]) => ({
                        category,
                        count
                    }))
                );

                setSentimentData(
                    (sentimentTrend?.timeline || []).map((point) => ({
                        timestamp: new Date(point.timestamp).toLocaleDateString(),
                        score: point.score
                    }))
                );

                setStats(dashboardStats || {});
                setAtRiskAccounts(Array.isArray(atRisk) ? atRisk : []);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const responseTimeHeatmap = useMemo(() => {
        const hours = Array.from({ length: 24 }, (_, i) => ({
            hour: `${i}:00`,
            count: 0
        }));

        (stats?.response_time_distribution || []).forEach((item) => {
            const hour = Number(item.hour);
            if (!Number.isNaN(hour) && hours[hour]) {
                hours[hour].count = item.count || 0;
            }
        });

        return hours;
    }, [stats]);

    const agentPerformance = useMemo(() => {
        const total = (stats?.replied || 0) + (stats?.escalated || 0) + (stats?.pending || 0);
        return {
            autoReplyRate: total ? ((stats?.replied || 0) / total) * 100 : 0,
            escalationRate: total ? ((stats?.escalated || 0) / total) * 100 : 0,
            avgConfidence: stats?.avg_confidence ?? 0,
        };
    }, [stats]);

    return (
        <div className="container">
            <h1>Analytics Dashboard</h1>
            <p className="muted">
                Live breakdown of agent final actions, category distribution, sentiment trends,
                and at-risk accounts.
            </p>

            {stats && (
                <div className="grid-3" style={{ marginBottom: 24 }}>
                    <div className="card">
                        <h3>Pending</h3>
                        <p style={{ fontSize: 24, fontWeight: 700 }}>{stats.pending ?? 0}</p>
                    </div>
                    <div className="card">
                        <h3>Replied</h3>
                        <p style={{ fontSize: 24, fontWeight: 700 }}>{stats.replied ?? 0}</p>
                    </div>
                    <div className="card">
                        <h3>Escalated</h3>
                        <p style={{ fontSize: 24, fontWeight: 700 }}>{stats.escalated ?? 0}</p>
                    </div>
                    <div className="card">
                        <h3>Critical</h3>
                        <p style={{ fontSize: 24, fontWeight: 700, color: "var(--critical)" }}>{stats.critical ?? 0}</p>
                    </div>
                    <div className="card">
                        <h3>Spam Filtered</h3>
                        <p style={{ fontSize: 24, fontWeight: 700 }}>{stats.spam_filtered ?? 0}</p>
                    </div>
                </div>
            )}

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <h2>Agent Final Actions</h2>
                    {loading ? (
                        <p className="muted">Loading…</p>
                    ) : actionData.length === 0 ? (
                        <div className="empty-state">No agent runs yet.</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={actionData}>
                                <XAxis dataKey="action" />
                                <YAxis allowDecimals={false} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#6d3bff" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                <div className="card">
                    <h2>Category Breakdown</h2>
                    {loading ? (
                        <p className="muted">Loading…</p>
                    ) : categoryData.length === 0 ? (
                        <div className="empty-state">No category data yet.</div>
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={categoryData}>
                                <XAxis dataKey="category" />
                                <YAxis allowDecimals={false} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#6d3bff" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </div>

            <div className="card" style={{ marginBottom: 24 }}>
                <h2>Sentiment Trend</h2>
                {loading ? (
                    <p className="muted">Loading…</p>
                ) : sentimentData.length === 0 ? (
                    <div className="empty-state">No sentiment data yet.</div>
                ) : (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={sentimentData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="timestamp" />
                            <YAxis domain={[-1, 1]} />
                            <Tooltip />
                            <Line type="monotone" dataKey="score" stroke="#6d3bff" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </div>

            <div className="grid-2" style={{ marginBottom: 24 }}>
                <div className="card">
                    <h2>Response Time Heatmap (by Hour)</h2>
                    {loading ? (
                        <p className="muted">Loading…</p>
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={responseTimeHeatmap}>
                                <XAxis dataKey="hour" />
                                <YAxis allowDecimals={false} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#6d3bff" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                <div className="card">
                    <h2>Agent Performance</h2>
                    {loading ? (
                        <p className="muted">Loading…</p>
                    ) : (
                        <div>
                            <p><strong>Auto-Reply Rate:</strong> {agentPerformance.autoReplyRate.toFixed(1)}%</p>
                            <p><strong>Escalation Rate:</strong> {agentPerformance.escalationRate.toFixed(1)}%</p>
                            <p><strong>Avg Confidence:</strong> {agentPerformance.avgConfidence.toFixed(2)}</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="card">
                <h2>At-Risk Accounts</h2>
                <p className="muted">
                    Senders with deteriorating sentiment (3+ consecutive negative emails).
                </p>
                {loading ? (
                    <p className="muted">Loading…</p>
                ) : atRiskAccounts.length === 0 ? (
                    <div className="empty-state">No at-risk accounts detected.</div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Sender</th>
                                <th>Timestamp</th>
                                <th>Sentiment Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {atRiskAccounts.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.sender}</td>
                                    <td>{item.timestamp}</td>
                                    <td>
                                        <span className="badge sentiment-negative">
                                            {item.score.toFixed(2)}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default AnalyticsPage;
