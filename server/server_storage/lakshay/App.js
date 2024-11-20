import React from "react";
import "./App.css";
import logo from "./logo.png"; // Import your logo

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <div className="logo-container">
                    <img src={logo} alt="CricFreak Logo" className="App-logo" />
                    <h1>CRICFREAK</h1>
                </div>
                <nav className="App-navbar">
                    <ul>
                        <li>
                            <a href="#">Teams</a>
                        </li>
                        <li>
                            <a href="#">Players</a>
                        </li>
                        <li>
                            <a href="#">Matches</a>
                        </li>
                        <li>
                            <a href="#">Tournaments</a>
                        </li>
                    </ul>
                </nav>
                <div className="search-account">
                    <input type="text" placeholder="Search..." className="search-bar" />
                    <button className="login-button">Login</button>
                </div>
            </header>
            <div className="App-body">
                <main className="App-content">
                    <h2>Welcome to Cricket Stats</h2>
                    <p>Select a section from the navigation bar to view more details.</p>
                </main>
            </div>
            <footer className="App-footer">
                <p>&copy; 2024 Cricket Stats</p>
            </footer>
        </div>
    );
}

export default App;
