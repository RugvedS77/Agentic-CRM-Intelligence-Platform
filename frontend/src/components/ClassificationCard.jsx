function ClassificationCard({ classification }) {

    if (!classification) {
        return (
            <div>
                <h2>Classification</h2>
                <p className="muted">No classification returned.</p>
            </div>
        );
    }

    const sentiment = (classification.sentiment || "neutral").toLowerCase();
    const urgency = (classification.urgency || "low").toLowerCase();

    return (
        <div>
            <h2>Classification</h2>

            <p>
                <strong>Category:</strong>{" "}
                <span className="badge">{classification.category}</span>
            </p>

            <p>
                <strong>Urgency:</strong>{" "}
                <span className={`badge urgency-${urgency}`}>{classification.urgency}</span>
            </p>

            <p>
                <strong>Sentiment:</strong>{" "}
                <span className={`badge sentiment-${sentiment}`}>
                    {classification.sentiment}
                    {typeof classification.sentiment_score === "number"
                        ? ` (${classification.sentiment_score.toFixed(2)})`
                        : ""}
                </span>
            </p>

            <p>
                <strong>Confidence:</strong>{" "}
                {typeof classification.confidence === "number"
                    ? classification.confidence.toFixed(2)
                    : classification.confidence}
            </p>

            <p>
                <strong>Requires Human:</strong>{" "}
                {classification.requires_human ? "Yes" : "No"}
            </p>

            {classification.escalation_reason && (
                <p>
                    <strong>Escalation Reason:</strong>{" "}
                    {classification.escalation_reason}
                </p>
            )}

            {classification.reasoning && (
                <p>
                    <strong>Reasoning:</strong>{" "}
                    {classification.reasoning}
                </p>
            )}

            {classification.detected_entities && (
                <div style={{ marginTop: 8 }}>
                    <strong>Entities:</strong>
                    <pre>{JSON.stringify(classification.detected_entities, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default ClassificationCard;