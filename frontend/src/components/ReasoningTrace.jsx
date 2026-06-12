function ReasoningTrace({ trace }) {
    if (!trace || trace.length === 0) {
        return <p className="muted">No reasoning steps recorded.</p>;
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {trace.map((step, index) => (
                <div
                    key={index}
                    style={{
                        border: "1px solid var(--border)",
                        borderRadius: 10,
                        background: "var(--surface)",
                        boxShadow: "var(--shadow)",
                        overflow: "hidden"
                    }}
                >
                    <div
                        style={{
                            background: "var(--accent-bg)",
                            borderBottom: "1px solid var(--border)",
                            padding: "10px 14px",
                            display: "flex",
                            alignItems: "center",
                            gap: 10
                        }}
                    >
                        <span
                            style={{
                                background: "var(--accent)",
                                color: "#fff",
                                borderRadius: 99,
                                padding: "2px 10px",
                                fontSize: 12,
                                fontWeight: 700
                            }}
                        >
                            #{index + 1}
                        </span>
                        <strong style={{ color: "var(--text-h)" }}>{step.thought || "Agent Step"}</strong>
                    </div>

                    <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
                        <div>
                            <div className="label" style={{ marginBottom: 4 }}>Action</div>
                            <div
                                style={{
                                    background: "var(--code-bg)",
                                    borderRadius: 6,
                                    padding: "8px 10px",
                                    fontSize: 13
                                }}
                            >
                                {typeof step.action === "string" ? (
                                    <code>{step.action}</code>
                                ) : (
                                    <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                                        {JSON.stringify(step.action, null, 2)}
                                    </pre>
                                )}
                            </div>
                        </div>

                        <div>
                            <div className="label" style={{ marginBottom: 4 }}>Observation</div>
                            <div
                                style={{
                                    background: "var(--code-bg)",
                                    borderRadius: 6,
                                    padding: "8px 10px",
                                    fontSize: 13
                                }}
                            >
                                {typeof step.observation === "string" ? (
                                    <span>{step.observation}</span>
                                ) : (
                                    <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                                        {JSON.stringify(step.observation, null, 2)}
                                    </pre>
                                )}
                            </div>
                        </div>

                        {step.next && (
                            <div>
                                <div className="label" style={{ marginBottom: 4 }}>Next</div>
                                <p style={{ margin: 0, fontSize: 14 }}>{step.next}</p>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default ReasoningTrace;
