import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
// import axios from "axios";

const Summarization = () => {
  // stored summaries in local storage to cache them, to fix re-rendering issue deleting summaries
  // potential for a better caching method
  const [googleSummary, setGoogleSummary] = useState(() => localStorage.getItem("googleSummary") || "Loading...");
  const [commentSummary, setCommentSummary] = useState(() => localStorage.getItem("commentSummary") || "Loading...");

  useEffect(() => {
    // pull summaries from cache or fetch them through the endpoint
    if (localStorage.getItem("googleSummary") && localStorage.getItem("commentSummary")) {
      setGoogleSummary(localStorage.getItem("googleSummary"));
      setCommentSummary(localStorage.getItem("commentSummary"));
      return;
    }

    const fetchSummaries = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/results");
        const data = await response.json();

        const google = data.google_summary;
        const comments = data.comment_summary;
      
        setGoogleSummary(google);
        setCommentSummary(comments);
      
        localStorage.setItem("googleSummary", google);
        localStorage.setItem("commentSummary", comments);
      } catch (error) {
        // alert("Error fetching summaries.");
        console.error("Error fetching summaries:", error); // fixed storage error
      }
    };

    fetchSummaries();
  }, []);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
      <main>
        <h1>Summarization Tool</h1>
        <div className="main-box">
          <p> Welcome to the summarization tool. Here we provide high-level summaries of our sources, so you can gain a clear and understandable overview without the noise, saving you hours of research.</p>
          <h2>Google Search Summary</h2>
          <p>{googleSummary}</p>
          <h2>YouTube Comment Summary</h2>
          <p>{commentSummary}</p>
        </div>
      </main>
    </motion.div>
  );
};

export default Summarization;
