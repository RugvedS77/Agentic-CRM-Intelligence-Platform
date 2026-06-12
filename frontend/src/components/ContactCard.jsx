import { useEffect, useState } from "react";
import { getContact } from "../api/agentApi";

function ContactCard({ email }) {
    const [contact, setContact] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!email) {
            setContact(null);
            return;
        }

        let cancelled = false;

        const fetchContact = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await getContact(email);
                if (!cancelled) {
                    setContact(data);
                }
            } catch (err) {
                if (!cancelled) {
                    console.error(err);
                    setError("Failed to load contact profile.");
                    setContact(null);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        fetchContact();

        return () => {
            cancelled = true;
        };
    }, [email]);

    return (
        <div className="card">
            <h3>Contact Profile</h3>
            {loading && <p className="muted">Loading contact…</p>}
            {error && <p className="error-text">{error}</p>}
            {!loading && !error && !contact && email && (
                <p className="muted">No CRM record found for <code>{email}</code>.</p>
            )}
            {!loading && !error && contact && (
                <div>
                    <p><strong>{contact.name || "Unknown"}</strong></p>
                    <p className="muted">{contact.email}</p>
                    {contact.company && <p>Company: {contact.company}</p>}
                    <p>Status: <span className="badge">{contact.status}</span></p>
                    <p>Account Value: ${contact.account_value?.toLocaleString?.() ?? contact.account_value ?? 0}</p>
                    <p>Churn Risk: {contact.churn_risk_score ?? 0}%</p>
                    <p>Subscription: {contact.subscription_tier}</p>
                    <p>Billing: {contact.billing_status}</p>
                    <p>Overdue Invoices: {contact.overdue_invoices}</p>
                    {contact.vip_status && <p className="badge urgency-critical">VIP</p>}
                </div>
            )}
        </div>
    );
}

export default ContactCard;
