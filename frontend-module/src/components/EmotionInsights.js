import React, { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import "../styles/emotion-insights.css";
import { motion } from "framer-motion";

import DataBreakdown from "./DataBreakdown";

ChartJS.register(ArcElement, Tooltip, Legend);

const EmotionInsights = ({ darkMode, highContrast }) => {
  const [emotionData, setEmotionData] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const chartTextColor = highContrast ? "yellow" : darkMode ? "#FFFFFF" : "#000000";

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/results")
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        // console.log("fetched data:", data);
        setEmotionData({
          product_name: data.product_name || {}, // fall back on empty variables for debugging, potential for caching
          overall_emotion_distribution: data.overall_emotion_distribution || {},
          // aspect_emotion_distribution: data.aspect_emotion_distribution || {},
          sentiment_distribution: data.sentiment_distribution || {},
          sentiment_comments: data.sentiment_comments || {},
          emotion_comments: data.emotion_comments || {},
          transcript_distributions: data.transcript_distributions || {},
          benefits_drawbacks: data.benefits_drawbacks || {},
          data_statistics: data.data_statistics || {},
          keywords_dict: data.keywords_dict || {}
        });
      })
      .catch((err) => {
        console.error("Error:", err);
      });
  }, []);

  if (!emotionData) {
    return <p>Loading emotion insights...</p>;
  }

  // removed functionality for aspect emotion dist due to diversity and accuracy
  const { product_name, overall_emotion_distribution, aspect_emotion_distribution, sentiment_distribution, sentiment_comments, emotion_comments, benefits_drawbacks, data_statistics, keywords_dict, transcript_distributions } = emotionData || {};

  const generateChartData = (distribution, label = "Distribution") => ({
    labels: Object.keys(distribution),
    datasets: [{label, data: Object.values(distribution), backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff", "#ff9f40", "#c9cbcf"]}],
  });

  const sentimentColors = {positive: "#36a2eb", negative: "#ff6384", neutral: "#ffce56"};
  
  const generateTranscriptChart = (distribution, label = "Distribution") => ({
    labels: Object.keys(distribution),
    datasets: [{label, data: Object.values(distribution), backgroundColor: Object.keys(distribution).map((key) => sentimentColors[key] || "#c9cbcf")}],
  });

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
      <main>
        <h1>YouTube Insights</h1>
        <div className="main-box">
          <p>We analyzed YouTube comments for relevant emotion insights on this product. Here you will be able to see various emotion insights into found YouTube video transcripts and comments for {product_name}.</p>

          {/* piecharts for transcripts sentiment distributions */}
          <h2>Video Transcript Sentiment Distribution</h2>
          <p>We've collected a lot of transcript text, here are the top 3 most mentioned product aspects from enthusisant opinions and their sentiment distribution:</p>
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "20px" }}>
            {Object.entries(transcript_distributions).map(([aspect, distribution]) => (
              <div key={aspect} style={{ width: "250px" }}>
                <h3 style={{ textAlign: "center", textTransform: "capitalize" }}>{aspect}</h3>
                <Pie data={generateTranscriptChart(distribution, `${aspect} Distribution`)} options={{ plugins: { legend: { labels: { color: chartTextColor, font: { size: 12}}}}}}/>
              </div>
            ))}
          </div>

          <h2>Transcript Keywords Word Cloud</h2>
          {keywords_dict && Object.keys(keywords_dict).length > 0 && (
            <>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginBottom: "2rem", justifyContent: "center" }}>
                {Object.entries(keywords_dict).map(([keyword, significance]) => {
                  // Simple scaling: base fontSize of 12 + 2 * significance
                  const fontSize = 3 + significance * 2.5;
                  const hue = Math.round((120 / 12) * significance); // 0..120
                  const color = `hsl(${hue}, 70%, 50%)`;

                  return (
                    <span key={keyword} style={{fontSize: fontSize, color: color, border: "1px solid transparent", padding: "2px 4px"}}>{keyword}</span>
                  );
                })}
              </div>
            </>
          )}

          <h2>Video Transcript Insights</h2>
          <p>Here are some key insights that we found from review videos discussing this product:</p>

          {/* benefits section */}
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ fontSize: "15px", marginBottom: "1rem"}}>Top Benefits</h3>
            <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
              {benefits_drawbacks[0].map((benefit, index) => (
                <li key={index} style={{ color: '#33cc33', marginBottom: '0.5rem', fontSize: '14px' }}>🟢 {benefit}</li>
              ))}
            </ul>
          </div>

          {/* drawbacks section */}
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ fontSize: "15px", marginBottom: "1rem"}}>Top Drawbacks</h3>
            <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
              {benefits_drawbacks[1].map((drawback, index) => (
                <li key={index} style={{ color: 'red', marginBottom: '0.5rem', fontSize: '14px' }}>❌ {drawback}</li>
              ))}
            </ul>
          </div>

          {/* emotion distribution pie chart */}
          <h2>Overall Comments Emotion Distribution</h2>
          <p>We've collected and processed a lot of comments, here is the emotion distribution across all comments and 3 comments falling under the top 3 mentioned categories:</p>
          <div style={{ width: "360px", margin: "1.5rem auto" }}>
            <Pie data={generateChartData(overall_emotion_distribution, "Emotion Distribution")} options={{ plugins: { legend: { labels: { color: chartTextColor, font: { size: 14 }}}}}}/>
          </div>

          {/* top 3 comments for top 3 emotions */}
          <h2>Comments for Top Emotions</h2>
          {/* added filter() to exclude sarcasm for display */}
          {Object.entries(emotion_comments).slice(0, 3).filter(([emotion]) => emotion.toLowerCase() !== "sarcasm").map(([emotion, comments]) => (
            <div key={emotion} style={{ margin: "1rem auto", textAlign: "left", width: "100%" }}>
              <h3 style={{ textTransform: "capitalize", fontSize: "1.15rem", marginBottom: "1rem" }}>{emotion}</h3>
              <ol style={{ marginLeft: "1.8rem", listStylePosition: "inside" }}>
                {comments.slice(0, 3).map((comment, index) => (
                  <li key={index} style={{ fontSize: "1rem" }}>{comment}</li>
                ))}
              </ol>
            </div>
          ))}

          {/* sentiment distribution section */}
          <h2>Overall Comments Sentiment Distribution</h2>
          <p>Here is the overall sentiment distribution across all of our found and filtered comments, and some examples for each category:</p>
          <div style={{ width: "350px", margin: "1.5rem auto" }}>
            <Pie data={generateChartData(sentiment_distribution, "Sentiment Distribution")} options={{ plugins: { legend: { labels: { color: chartTextColor, font: { size: 14}}}}}}/>
          </div>

          {/* top 3 comments for each sentiment category (minus mixed) */}
          <div>
            <h3 style={{ textTransform: "capitalize", fontSize: "1.15rem", margin: "1rem auto" }}>Positive Comments</h3>
            <ol style={{ marginLeft: "1.8rem" }}>
              {sentiment_comments.positive.slice(0, 3).map((comment, index) => (
                <li key={index} style={{ fontSize: "1rem" }}>{comment}</li>
              ))}
            </ol>
            
            {/* - removed, not enough mixed comments for each product to display so none ever display
            <h3 style={{ textTransform: "capitalize", fontSize: "1.15rem", margin: "1rem auto" }}>Mixed Comments</h3>
            <ol style={{ marginLeft: "1.8rem" }}>
              {sentiment_comments.mixed?.slice(0, 3).map((comment, index) => (
                <li key={index} style={{ fontSize: "1rem" }}>{comment}</li>
              ))}
            </ol>
            */}

            <h3 style={{ textTransform: "capitalize", fontSize: "1.15rem", margin: "1rem auto" }}>Negative Comments</h3>
            <ol style={{ marginLeft: "1.8rem" }}>
              {sentiment_comments.negative.slice(0, 3).map((comment, index) => (
                <li key={index} style={{ fontSize: "1rem" }}>{comment}</li>
              ))}
            </ol>
          </div>
        </div>

        <button className="data-breakdown-btn" onClick={() => setShowModal(!showModal)}>Data Breakdown</button>
        <DataBreakdown isOpen={showModal} onClose={() => setShowModal(false)} stats={data_statistics}/>
      </main>
    </motion.div>
  );
};

export default EmotionInsights;