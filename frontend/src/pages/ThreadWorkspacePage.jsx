import { useEffect, useState } from "react";
import ContactCard from "../components/ContactCard";
import ThreadTimeline from "../components/ThreadTimeline";
import {
    getThread,
    getInbox,
    getContact,
    sendManualReply,
    updateDraft,
    approveDraft,
    ragSearch
} from "../api/agentApi";

function highlightEntities(text, entities = []) {
    if (!entities || entities.length === 0) return text;
    const sorted = [...entities].sort((a, b) => (b.value || "").length - (a.value || "").length);
    let result = text;
    sorted.forEach((entity) => {
        const value = entity.value;
        if (!value) return;
        const escaped = value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const regex = new RegExp(escaped, "gi");
        result = result.replace(regex, (match) => `<mark>${match}</mark>`);
    });
    return result;
}

function ThreadWorkspacePage() {
    const [threadId, setThreadId] = useState("thread_bob_outage");
    const [thread, setThread] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Action area state
    const [actionLoading, setActionLoading] = useState(false);
    const [actionMessage, setActionMessage] = useState(null);
    const [replyBody, setReplyBody] = useState("");
    const [draftId, setDraftId] = useState("");
    const [draftContent, setDraftContent] = useState("");

    // Intelligence state
    const [ragResults, setRagResults] = useState(null);
    const [ragLoading, setRagLoading] = useState(false);
    const [webIntel, setWebIntel] = useState(null);
    const [webIntelLoading, setWebIntelLoading] = useState(false);

    const handleFetch = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            setError(null);
            const data = await getThread(threadId);
            setThread(data);
        } catch (err) {
            console.error(err);
            setThread(null);
            setError("Thread not found. Check the thread ID and try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleSendReply = async () => {
        if (!thread?.emails?.[0]?.message_id) return;
        try {
            setActionLoading(true);
            setActionMessage(null);
            await sendManualReply(thread.emails[0].message_id, replyBody, "user");
            setActionMessage({ type: "success", text: "Reply sent successfully." });
            setReplyBody("");
        } catch (err) {
            console.error(err);
            setActionMessage({ type: "error", text: "Failed to send reply." });
        } finally {
            setActionLoading(false);
        }
    };

    const handleEditDraft = async () => {
        if (!draftId) return;
        try {
            setActionLoading(true);
            setActionMessage(null);
            await updateDraft(draftId, draftContent);
            setActionMessage({ type: "success", text: "Draft updated." });
            setDraftContent("");
            setDraftId("");
        } catch (err) {
            console.error(err);
            setActionMessage({ type: "error", text: "Failed to update draft." });
        } finally {
            setActionLoading(false);
        }
    };

    const handleApproveDraft = async () => {
        if (!draftId) return;
        try {
            setActionLoading(true);
            setActionMessage(null);
            await approveDraft(draftId, "user");
            setActionMessage({ type: "success", text: "Draft approved and sent." });
            setDraftId("");
        } catch (err) {
            console.error(err);
            setActionMessage({ type: "error", text: "Failed to approve draft." });
        } finally {
            setActionLoading(false);
        }
    };

    const handleEscalate = async () => {
        if (!thread?.emails?.[0]?.message_id) return;
        try {
            setActionLoading(true);
            setActionMessage(null);
            await sendManualReply(
                thread.emails[0].message_id,
                "This email has been escalated to human support for further review.",
                "user"
            );
            setActionMessage({ type: "success", text: "Email escalated to human support." });
        } catch (err) {
            console.error(err);
            setActionMessage({ type: "error", text: "Failed to escalate." });
        } finally {
            setActionLoading(false);
        }
    };

    const handleMarkSpam = async () => {
        if (!thread?.emails?.[0]?.message_id) return;
        try {
            setActionLoading(true);
            setActionMessage(null);
            await sendManualReply(
                thread.emails[0].message_id,
                "This email has been marked as spam and will be filtered.",
                "user"
            );
            setActionMessage({ type: "success", text: "Email marked as spam." });
        } catch (err) {
            console.error(err);
            setActionMessage({ type: "error", text: "Failed to mark as spam." });
        } finally {
            setActionLoading(false);
        }
    };

    const handleRagSearch = async () => {
        const query = thread?.thread?.subject || threadId;
        try {
            setRagLoading(true);
            setRagResults(null);
            const data = await ragSearch(query);
            setRagResults(data);
        } catch (err) {
            console.error(err);
            setRagResults(null);
        } finally {
            setRagLoading(false);
        }
    };

    const handleWebIntel = async () => {
        const sender = thread?.emails?.[0]?.sender || "";
        const domain = sender.split("@")[1]?.split(".")[0] || "SenAI";
        try {
            setWebIntelLoading(true);
            setWebIntel(null);
            const res = await fetch(`/intelligence/reputation?company_name=${encodeURIComponent(domain)}`);
            const data = await res.json();
            setWebIntel(data);
        } catch (err) {
            console.error(err);
            setWebIntel(null);
        } finally {
            setWebIntelLoading(false);
        }
    };

    useEffect(() => {
        if (thread) {
            handleRagSearch();
            handleWebIntel();
        }
    }, [thread]);

    const enrichedEmails = (thread?.emails || []).map((email) => {
        const entities = Array.isArray(email.detected_entities) ? email.detected_entities : [];
        const highlightedBody = highlightEntities(email.body || "", entities);
        return {
            ...email,
            highlightedBody,
            sentimentIndicator: email.sentiment ? (
                <span className={`badge sentiment-${String(email.sentiment).toLowerCase()}`}>
                    {email.sentiment}
                </span>
            ) : null,
        };
    });

    return (
        <div className="container">
            <h1>Thread Workspace</h1>

            <form onSubmit={handleFetch} className="grid-2" style={{ alignItems: "end", marginBottom: 16 }}>
                <div className="field">
                    <label>Thread ID</label>
                    <input
                        type="text"
                        value={threadId}
                        onChange={(e) => setThreadId(e.target.value)}
                        placeholder="e.g. thread_bob_outage"
                    />
                </div>
                <div>
                    <button type="submit" disabled={loading}>
                        {loading ? "Loading…" : "Load Thread"}
                    </button>
                </div>
            </form>

            {error && (
                <div className="card"><p className="error-text">{error}</p></div>
            )}

            {thread && (
                <div className="workspace">
                    <div className="card">
                        <h3>{thread.thread?.subject || threadId}</h3>

                        {thread.thread?.summary && (
                            <p className="muted">{thread.thread.summary}</p>
                        )}

                        <ThreadTimeline emails={enrichedEmails} />
                    </div>

                    <div>
                        <ContactCard email={thread.emails?.[0]?.sender} />

                        <div className="card" style={{ marginTop: 16 }}>
                            <h3>Actions</h3>
                            {actionMessage && (
                                <p className={actionMessage.type === "error" ? "error-text" : ""}>
                                    {actionMessage.text}
                                </p>
                            )}
                            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                <button onClick={handleSendReply} disabled={actionLoading || !replyBody}>
                                    {actionLoading ? "Working…" : "Approve & Send"}
                                </button>
                                <textarea
                                    rows={3}
                                    placeholder="Reply body..."
                                    value={replyBody}
                                    onChange={(e) => setReplyBody(e.target.value)}
                                />
                                <div style={{ display: "flex", gap: 8 }}>
                                    <input
                                        type="text"
                                        placeholder="Draft ID"
                                        value={draftId}
                                        onChange={(e) => setDraftId(e.target.value)}
                                        style={{ flex: 1 }}
                                    />
                                    <button
                                        className="secondary"
                                        onClick={handleApproveDraft}
                                        disabled={actionLoading || !draftId}
                                    >
                                        Approve Draft
                                    </button>
                                </div>
                                <textarea
                                    rows={2}
                                    placeholder="Updated draft content..."
                                    value={draftContent}
                                    onChange={(e) => setDraftContent(e.target.value)}
                                />
                                <button
                                    className="secondary"
                                    onClick={handleEditDraft}
                                    disabled={actionLoading || !draftId || !draftContent}
                                >
                                    Edit Draft
                                </button>
                                <button className="secondary" onClick={handleEscalate} disabled={actionLoading}>
                                    Escalate
                                </button>
                                <button className="secondary" onClick={handleMarkSpam} disabled={actionLoading}>
                                    Mark Spam
                                </button>
                            </div>
                        </div>

                        <div className="card" style={{ marginTop: 16 }}>
                            <h3>RAG Context</h3>
                            {ragLoading && <p className="muted">Loading…</p>}
                            {!ragLoading && ragResults && (
                                <div>
                                    <p className="muted">Query: {ragResults.query}</p>
                                    {ragResults.results?.length > 0 ? (
                                        ragResults.results.map((r, i) => (
                                            <div key={i} className="trace-step">
                                                <div className="label">Source: {r.source}</div>
                                                <pre style={{ whiteSpace: "pre-wrap" }}>{r.content}</pre>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="muted">No RAG chunks retrieved.</p>
                                    )}
                                </div>
                            )}
                        </div>

                        <div className="card" style={{ marginTop: 16 }}>
                            <h3>Web Intelligence</h3>
                            {webIntelLoading && <p className="muted">Loading…</p>}
                            {!webIntelLoading && webIntel && (
                                <div>
                                    {webIntel.status ? (
                                        <p className="muted">{webIntel.status}</p>
                                    ) : (
                                        <div>
                                            <p><strong>Source:</strong> {webIntel.source}</p>
                                            <pre style={{ whiteSpace: "pre-wrap" }}>
                                                {JSON.stringify(webIntel.data, null, 2)}
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {!thread && !error && !loading && (
                <div className="empty-state">
                    Enter a thread ID (e.g. thread_bob_outage, thread_karen_refund) and click
                    "Load Thread" to view its conversation history.
                </div>
            )}
        </div>
    );
}

export default ThreadWorkspacePage;
