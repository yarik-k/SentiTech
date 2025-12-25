import React from "react";
import "../styles/data-breakdown.css";
import { motion, AnimatePresence } from "framer-motion";

// dummy data for testing popup
// const dummyStats = {
//   google_sites_processed: 30,
//   sentences_analyzed: 500,
//   youtube_comments_total: 1000,
//   youtube_comments_filtered: 200,
//   transcript_word_count: 10000,
//   cleaned_transcript_word_count: 2000,
// }

const DataBreakdown = ({ isOpen, onClose, stats }) => { // stats undefined?
  if (!isOpen) return null;
  // console.log("extracted stats", stats);

  return (
    <AnimatePresence>
      <motion.div className="overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}>
        <motion.div className="content" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
          <button className="close-btn" onClick={onClose}>✖</button>
          <h2>Data Breakdown</h2>

          <h3>🔎 Google Data</h3>
          <p>Google Sites Processed: <span className="green">{stats.google_sites_processed}</span></p>
          <p>Sentences Analyzed: <span className="green">{stats.sentences_analyzed}</span></p>

          <h3>🎥 YouTube Data</h3>
          <p>Total YouTube Comments Found: <span className="red">{stats.youtube_comments_total}</span></p>
          <p>Total YouTube Comments After Filtering: <span className="green">{stats.youtube_comments_filtered}</span></p>
          <p>Total Volume of Transcript Data Found: <span className="red">{stats.transcript_word_count}</span> words</p>
          <p>Total Volume of Transcript Data After Filtering: <span className="green">{stats.cleaned_transcript_word_count}</span> words</p>
          {/* options for deeper breakdown: product names detected, basic sentiment info */}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DataBreakdown;