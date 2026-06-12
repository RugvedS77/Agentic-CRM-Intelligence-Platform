function ThreadTimeline({ emails }) {

    if (!emails || emails.length === 0) {
        return <p className="muted">No emails found in this thread.</p>;
    }

    return (
        <div>
            <h3>Conversation ({emails.length})</h3>
            {emails.map((email, i) => (
                <div key={email.message_id || i} className="trace-step">
                    <div className="label">
                        {email.sender} — {email.timestamp}
                        {email.sentimentIndicator && (
                            <span style={{ marginLeft: 8 }}>{email.sentimentIndicator}</span>
                        )}
                    </div>
                    <p><strong>{email.subject}</strong></p>
                    <p
                        style={{ whiteSpace: "pre-wrap" }}
                        dangerouslySetInnerHTML={{ __html: email.highlightedBody || email.body }}
                    />
                </div>
            ))}
        </div>
    );
}

export default ThreadTimeline;
