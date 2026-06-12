function ToolResults({ results }) {

    return (
        <div>
            <h2>Tool Results</h2>

            {results && results.length > 0 ? (
                results.map((item, index) => (
                    <div key={index} className="trace-step">
                        <div className="label">{item.tool}</div>
                        <pre>{JSON.stringify(item.result, null, 2)}</pre>
                    </div>
                ))
            ) : (
                <p className="muted">No tools executed (dry run or no actions required).</p>
            )}
        </div>
    );
}

export default ToolResults;
