import { useState } from "react";

function EmailForm({ onSubmit, loading }) {

    const [formData, setFormData] = useState({
        email_id: "msg_060",
        sender_email: "bob.jones@enterprise.net",
        email_body: "",
        thread_context: "",
        dry_run: false
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;

        setFormData({
            ...formData,
            [name]: type === "checkbox" ? checked : value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <form onSubmit={handleSubmit}>

            <div className="grid-2">
                <div className="field">
                    <label>Email ID</label>
                    <input
                        type="text"
                        name="email_id"
                        value={formData.email_id}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="field">
                    <label>Sender Email</label>
                    <input
                        type="email"
                        name="sender_email"
                        value={formData.sender_email}
                        onChange={handleChange}
                        required
                    />
                </div>
            </div>

            <div className="field">
                <label>Email Body</label>
                <textarea
                    name="email_body"
                    rows="6"
                    placeholder="Paste the email content here…"
                    value={formData.email_body}
                    onChange={handleChange}
                    required
                />
            </div>

            <div className="field">
                <label>Thread Context (optional)</label>
                <textarea
                    name="thread_context"
                    rows="3"
                    placeholder="Prior emails in this thread, for context…"
                    value={formData.thread_context}
                    onChange={handleChange}
                />
            </div>

            <div className="field checkbox-row">
                <input
                    type="checkbox"
                    id="dry_run"
                    name="dry_run"
                    checked={formData.dry_run}
                    onChange={handleChange}
                />
                <label htmlFor="dry_run" style={{ margin: 0 }}>
                    Dry run (plan only, don't execute tools)
                </label>
            </div>

            <button type="submit" disabled={loading}>
                {loading ? "Running…" : "Run Agent"}
            </button>

        </form>
    );
}

export default EmailForm;