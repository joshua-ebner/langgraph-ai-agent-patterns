import { Link, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import PatternPage from "./pages/PatternPage";

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="brand">
          LangGraph Agent Patterns
        </Link>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/patterns/:patternId" element={<PatternPage />} />
        </Routes>
      </main>
    </div>
  );
}
