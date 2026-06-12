import { NavLink } from "react-router-dom";

function Navbar() {
    return (
        <nav className="navbar">
            <span className="brand">SenAI CRM Agent</span>

            <NavLink to="/" end className={({ isActive }) => isActive ? "active" : ""}>
                Inbox
            </NavLink>

            <NavLink to="/agent" className={({ isActive }) => isActive ? "active" : ""}>
                Agent Playground
            </NavLink>

            <NavLink to="/runs" className={({ isActive }) => isActive ? "active" : ""}>
                Runs
            </NavLink>

            <NavLink to="/analytics" className={({ isActive }) => isActive ? "active" : ""}>
                Analytics
            </NavLink>

            <NavLink to="/thread-demo" className={({ isActive }) => isActive ? "active" : ""}>
                Thread Workspace
            </NavLink>
        </nav>
    );
}

export default Navbar;