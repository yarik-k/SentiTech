import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { Chart, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import "../styles/feature-sentiment.css";
import { motion } from "framer-motion";
import DataBreakdown from "./DataBreakdown";

Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const FeatureSentiment = ({ darkMode, highContrast }) => {
  const [sentimentData, setSentimentData] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const chartTextColor = highContrast ? "yellow" : darkMode ? "#FFFFFF" : "#000000";

  useEffect(() => {
    fetch("http://localhost:8000/api/results")
      .then((response) => response.json())
      .then((data) => setSentimentData(data))
      .catch((error) => console.error("Error:", error));
  }, []);

  if (!sentimentData) {
    return <p>Loading sentiment data...</p>; // added for each file is requests fail
  }

  const featureFrequencies = sentimentData.feature_frequencies;

  // added sorted data for clarity and UX
  const entries = Object.entries(featureFrequencies)
  const sortedFeatures = entries.sort((a, b) => b[1] - a[1]);
  const sortedLabels = sortedFeatures.map((entry) => entry[0]);
  const sortedValues = sortedFeatures.map((entry) => entry[1]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
      <main className="feature-sentiment-container">
        <h1>Feature Sentiment Analysis</h1>
        <div className="main-box">
          {sentimentData && (
            <>
              <p>We analyzed a bunch of Google sources so you don't have to, here's what we found from discussions.</p>
              <p>This section provides a detailed sentiment breakdown based on the features mentioned of the product you have entered, helping you understand how users feel about different aspects of{" "}{sentimentData.product_name}.</p>
              <h2>Overview</h2>
              <p>✅ Positive Sentiment: {Math.round(sentimentData.positive_percentage)}% of user opinions expressed satisfaction.</p>
              <p>❌ Negative Sentiment: {Math.round(sentimentData.negative_percentage)}% of user opinions highlighted concerns.</p>
              <p>➖ Neutral Sentiment: {Math.round(sentimentData.neutral_percentage)}% of user opinions provided balanced feedback.</p>

              <h2>Feature Sentiment Breakdown</h2>
              <table className="sentiment-table">
                {/* headings */}
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th>Sentiment Score</th>
                    <th>Star Rating</th>
                    <th>Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {sentimentData.features.map((feature, index) => (
                    <tr key={index}>
                      <td>{feature.feature}</td>
                      <td>
                        <div className="sentiment-bar-container">
                          {/* fixed sentiment scores -> sentiment bars for user experience */}
                          <div className="sentiment-bar" style={{ width: `${(feature.sentiment_score * 100).toFixed(2)}%`}}></div>
                        </div>
                        <span className="sentiment-score-text">{(feature.sentiment_score * 100).toFixed(0)}%</span>
                      </td>
                      <td>{"⭐".repeat(feature.star_rating)}</td>
                      <td>{feature.example_sentence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <h2>Feature Mention Frequency</h2>
              <div className="chart-container">
                {/* fixed options finally with docs */}
                <Bar data={{ labels: sortedLabels, datasets: [{label: "Feature Mentions", data: sortedValues, backgroundColor: "#6C9BCF", borderColor: chartTextColor, borderWidth: 0.6, borderRadius: 6 }]}}
                    options={{ responsive: true, maintainAspectRatio: false, scales: { 
                    x: { title: { display: true, text: "Features", color: chartTextColor }, ticks: { color: chartTextColor }},
                    y: { title: { display: true, text: "Mentions", color: chartTextColor }, beginAtZero: true, min: 0, max: Math.ceil(Math.max(...sortedValues) / 5) * 5, ticks: { color: chartTextColor, stepSize: 5, precision: 0, callback: (value) => (value % 5 === 0 ? value : "")}}}, // by 5 for precision, larger data volumes may need 10 or 15 increments
                    plugins: { legend: { display: true, position: "top", labels: { color: chartTextColor }}}}}
                />
              </div>
            </>
          )}
        </div>
        <button className="data-breakdown-btn" onClick={() => setShowModal(!showModal)}>Data Breakdown</button>
        <DataBreakdown isOpen={showModal} onClose={() => setShowModal(false)} stats={sentimentData.data_statistics}/>
      </main>
    </motion.div>
  );
};

export default FeatureSentiment;
