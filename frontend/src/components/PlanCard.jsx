function PlanCard({ plan }) {

    return (
        <div>
            <h2>Plan</h2>

            {plan && plan.length > 0 ? (
                <ol>
                    {plan.map((tool, index) => (
                        <li key={index}>
                            <code>{tool}</code>
                        </li>
                    ))}
                </ol>
            ) : (
                <p className="muted">No tools planned.</p>
            )}
        </div>
    );
}

export default PlanCard;
