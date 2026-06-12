import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({
    baseURL: API_BASE,
    headers: {
        "Content-Type": "application/json"
    }
});

// Raw axios calls (return full response object)
export const post = (path, data, options = {}) => {
    return client.post(path, data, options);
};

export const get = (path, options = {}) => {
    return client.get(path, options);
};

// Convenience helpers that return response.data directly
export const runAgent = async (payload) => {
    const res = await client.post("/agent/run", payload);
    return res.data;
};

export const getAgentRuns = async () => {
    const res = await client.get("/agent/runs");
    return res.data;
};

export const getAgentRun = async (runId) => {
    const res = await client.get(`/agent/runs/${runId}`);
    return res.data;
};

export const getThread = async (threadId) => {
    const res = await client.get(`/threads/${threadId}`);
    return res.data;
};

export const ragSearch = async (query) => {
    const res = await client.get("/rag/search", { params: { q: query } });
    return res.data;
};

export const getInbox = async () => {
    const res = await client.get("/inbox/");
    return res.data;
};

export const getContact = async (email) => {
    const res = await client.get(`/contacts/${encodeURIComponent(email)}`);
    return res.data;
};

export const sendManualReply = async (emailId, replyBody, userId) => {
    const res = await client.post(`/respond/${encodeURIComponent(emailId)}`, {
        reply_body: replyBody,
        user_id: userId
    });
    return res.data;
};

export const updateDraft = async (draftId, proposedContent) => {
    const res = await client.patch(`/drafts/${draftId}`, {
        proposed_content: proposedContent
    });
    return res.data;
};

export const approveDraft = async (draftId, userId) => {
    const res = await client.post(`/drafts/${draftId}/approve`, {
        user_id: userId
    });
    return res.data;
};

export const getSentimentTrend = async (sender, days = 30) => {
    const res = await client.get("/analytics/sentiment-trend", {
        params: { sender, days }
    });
    return res.data;
};

export const getCategoryBreakdown = async () => {
    const res = await client.get("/analytics/category-breakdown");
    return res.data;
};

export const getDashboardStats = async () => {
    const res = await client.get("/analytics/dashboard/stats");
    return res.data;
};

export const getAtRiskAccounts = async () => {
    const res = await client.get("/analytics/at-risk-accounts");
    return res.data;
};

export const getJobStatus = async (jobId) => {
    const res = await client.get(`/api/status/${encodeURIComponent(jobId)}`);
    return res.data;
};

export const getThreadsByContact = async (contactEmail) => {
    const res = await client.get(`/threads/${encodeURIComponent(contactEmail)}`);
    return res.data;
};

export const dryRunAgent = async (emailId) => {
    const res = await client.post(`/agent/dry-run/${encodeURIComponent(emailId)}`);
    return res.data;
};

export const startStream = async (speed = 1) => {
    const res = await fetch(`${API_BASE}/api/stream/start?speed=${speed}`);
    return res;
};

export const stopStream = async () => {
    const res = await client.post("/api/stream/stop");
    return res.data;
};

export const getStreamStatus = async () => {
    const res = await client.get("/api/stream/status");
    return res.data;
};

export const bulkArchive = async (emailIds, userId) => {
    const res = await client.post("/bulk/archive", { email_ids: emailIds, user_id: userId });
    return res.data;
};

export const bulkMarkSpam = async (emailIds, userId) => {
    const res = await client.post("/bulk/spam", { email_ids: emailIds, user_id: userId });
    return res.data;
};

export const bulkAssign = async (emailIds, userId) => {
    const res = await client.post("/bulk/assign", { email_ids: emailIds, user_id: userId });
    return res.data;
};

export default {
    post,
    get,
    runAgent,
    getAgentRuns,
    getAgentRun,
    getThread,
    ragSearch,
    getInbox,
    getContact,
    sendManualReply,
    updateDraft,
    approveDraft,
    getSentimentTrend,
    getCategoryBreakdown,
    getDashboardStats,
    getJobStatus,
    getThreadsByContact,
    dryRunAgent,
    startStream,
    stopStream,
    getStreamStatus,
    bulkArchive,
    bulkMarkSpam,
    bulkAssign
};
