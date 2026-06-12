import { useEffect, useState } from "react";

import EmailForm from "../components/EmailForm";
import ClassificationCard from "../components/ClassificationCard";
import PlanCard from "../components/PlanCard";
import ToolResults from "../components/ToolResults";
import ReasoningTrace from "../components/ReasoningTrace";

import { runAgent } from "../api/agentApi";

const STORAGE_KEY = "senai_agent_last_result";

function AgentPage() {
    const [result, setResult] = useState(() => {
        try {
            const stored = sessionStorage.getItem(STORAGE_KEY);
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (result) {
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(result));
            } catch {
                // ignore storage errors
            }
        }
    }, [result]);

    const handleSubmit = async (formData) => {
        try {
            setLoading(true);
            setError(null);
            setResult(null);

            const data = await runAgent(formData);
            setResult(data);
        } catch (err) {
            console.error(err);
            setError(
                err?.response?.data?.message ||
                err?.message ||
                "Failed to run agent."
            );
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setResult(null);
        setError(null);
        try {
            sessionStorage.removeItem(STORAGE_KEY);
        } catch {
            // ignore
        }
    };

    return (
        <div className="container">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                    <h1>SenAI Autonomous Triage Agent</h1>
                    <p className="muted">
                        Submit an inbound email and watch the agent classify it, ground itself
                        with RAG context, plan its actions, and walk through its reasoning trace.
                    </p>
                </div>
                {result && (
                    <button className="secondary" onClick={handleClear}>
                        Clear Result
                    </button>
                )}
            </div>

            <div className="card" style={{ marginTop: 16 }}>
                <EmailForm onSubmit={handleSubmit} loading={loading} />
            </div>

            {loading && <p className="muted">Running agent…</p>}

            {error && (
                <div className="card">
                    <p className="error-text">{error}</p>
                </div>
            )}

            {result && (
                <>
                    <div className="grid-2">
                        <div className="card">
                            <ClassificationCard classification={result.classification} />
                        </div>
                        <div className="card">
                            <PlanCard plan={result.plan} />
                        </div>
                    </div>

                    <div className="card">
                        <ToolResults results={result.tool_results} />
                    </div>

                    <div className="card">
                        <ReasoningTrace trace={result.reasoning_trace} />
                    </div>
                </>
            )}
        </div>
    );
}

export default AgentPage;
