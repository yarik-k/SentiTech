import React, { useState, useEffect } from "react";
import { NavLink } from "react-router-dom";
import "../styles/index.css";
import logo from "../images/logo.png";
import { motion, AnimatePresence } from "framer-motion";
// import clsx from "clsx"; - switch to clsx for class management

function Sidebar({ searchCompleted, searchLoading }) {
  const [verdictOpen, setVerdictOpen] = useState(false);
  const [verdict, setVerdict] = useState([]);

  const sidebarClass = searchCompleted ? "sidebar sidebar-expanded" : "sidebar sidebar-collapsed";
  const linkClass = searchCompleted ? "slide-in" : "slide-offscreen";

  const handleVerdictToggle = () => {
    // console.log("Verdict dropdown toggled:", verdictOpen);
    setVerdictOpen((prev) => !prev);
  };

  useEffect(() => {
    // real-time verdict fetch
    // change out for caching logic to reduce requests and potential errors
    if (verdictOpen) {
      fetch("http://localhost:8000/api/results") 
        .then((response) => {
          return response.json() // improve handling of GPT output - could be inconsistent
        })
        .then((data) => {
          setVerdict(data.tldr_lines || [])
        })
        .catch((err) => {
          console.error("Error:", err)});
    }
  }, [verdictOpen]);

  return (
    <aside>
        <div className="toggle">
          <div className="logo">
            <img src={logo} alt="SentiTech Logo" />
            <h2 translate="no">Senti<span className="tech">Tech</span></h2>
          </div>
        </div>
        {/* search complete -> show TLDR button -> pressed TLDR button -> show dropdown popup done */}
        {searchCompleted && (
          <div className="quick-verdict-container">
            <button className="quick-verdict-btn" onClick={handleVerdictToggle}>
              Quick Verdict
            </button>
            <AnimatePresence>
              {verdictOpen && (
                <motion.div className="quick-verdict-dropdown" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
                  <h2>Our Quick Verdict</h2>
                  <h3>⚡ Short Summary</h3>
                  <p>{verdict[0]}</p>
                  <h3>⚠️ Risk Assessment</h3>
                  <p>{verdict[1]}</p>
                  <h3>⚖️ Verdict</h3>
                  <p>{verdict[2]}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      {/* dynamic sidebar logic works now for collapsed and expanded version using CSS styles */}
      <div className={sidebarClass} style={searchLoading ? { pointerEvents: "none" } : {}}>
        <NavLink to="/get-started">
          <span className="material-symbols-outlined" translate="no">home</span>
          <h3>Get Started</h3>
        </NavLink>
        <div className="new-tabs-container">
          <NavLink to="/feature-sentiment-analysis" className={linkClass}>
            <span className="material-symbols-outlined" translate="no">sort</span>
            <h3>Feature Sentiment Analysis</h3>
          </NavLink>
          <NavLink to="/emotion-insights" className={linkClass}>
            <span className="material-symbols-outlined" translate="no">emoji_language</span>
            <h3>YouTube Insights</h3>
          </NavLink>
          <NavLink to="/summarization" className={linkClass}>
            <span className="material-symbols-outlined" translate="no">summarize</span>
            <h3>Summarization</h3>
          </NavLink>
          <NavLink to="/comparison-tool" className={linkClass}>
            <span className="material-symbols-outlined" translate="no">text_compare</span>
            <h3>Comparison Tool</h3>
          </NavLink>
        </div>
        <NavLink to="/settings" className="settings">
            <span className="material-symbols-outlined" translate="no">settings</span>
            <h3>Settings</h3>
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;
