import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import "../styles/get-started.css";
import { getAllProducts } from "./parseProducts.js";
import { motion } from "framer-motion";

function GetStarted({ setSearchCompleted, setSearchLoading }) {
  const [loading, setLoading] = useState(false);
  const [productInput, setProductInput] = useState("");
  const [progress, setProgress] = useState(0);
  const [suggestions, setSuggestions] = useState([]);
  const [searchParams] = useSearchParams();
  // const [notification, setNotification] = useState(false);
  // const [animationTriggered, setAnimationTriggered] = useState(false); implement animation when done loading

  const productName = searchParams.get("product") || "";
  const hasSearched = useRef(false);
  const allProducts = getAllProducts();

  {/* fixed 2 types of runs - auto run from comparison table SentiTech button or manual search from current page */}
  useEffect(() => {
    if (productName && !hasSearched.current) {
      hasSearched.current = true;

      setProductInput(productName);
      runSearch(productName, true);
    }
  }, [productName]);

  const runSearch = async (name, autoRun = false) => {
    setSuggestions([]);
    setSearchCompleted(false);
    localStorage.removeItem("googleSummary"); // remove these if refactored google storage implemented (later)
    localStorage.removeItem("commentSummary");

    let searchQuery = autoRun ? name : productInput;
    searchQuery = searchQuery.trim();
    if (!searchQuery) {
      alert("Please enter a product name.");
      return;
    }

    setLoading(true);
    setSearchLoading(true);
    pollProgress();
    setProductInput("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product: name }),
      });
      if (response.ok) {
        console.log("Search completed!");

        await pollResults();

        setSearchCompleted(true);
      }
    } catch (error) {
      console.error("Fetch error:", error);
    }
    setLoading(false);
    setSearchLoading(false);
  };

  const pollResults = async () => {
    let attempts = 0;
    const maxAttempts = 15;

    while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 100)); // Wait 2 seconds

        try {
            const response = await fetch("http://127.0.0.1:8000/api/results");
            const data = await response.json();

            if (data.status !== "processing") {
                console.log("Results are now cached!", data);
                return;
            }

            console.log("Attempt: " + attempts + 1);
        } catch (error) {
            console.error("Polling error:", error);
        }
        attempts++;
    }
    console.warn("Polling timed out.");
  };

  const pollProgress = async () => {
    let attempts = 0;
    const maxAttempts = 1500;
  
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 200)); // Poll every 200ms
  
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/progress`);
        const data = await response.json();

  
        // Compute average progress
        const modules = ["google", "youtube", "summary", "comparison"];
        const total = modules.reduce((sum, mod) => sum + (data[mod] || 0), 0);
        const percentComplete = Math.round((total / modules.length) * 0.9); // doesn't go past 90%, leave time for polling and caching
  
        setProgress(percentComplete);

        if (data.completed) {
          return;
        }

      } catch (error) {
        console.error("Progress polling error:", error);
      }
  
      attempts++;
    }
  };

  const handleInputChange = (value) => {
    setProductInput(value)
    
    if (!value) {
      setSuggestions([]);
      return;
    }

    // basic, implement better if needed
    const matches = allProducts.filter((product) => {
      return product.toLowerCase().includes(value.toLowerCase());
    });

    const topSuggestions = matches.slice(0, 7);
    setSuggestions(topSuggestions);
  };

  const handleSuggestionClick = (suggestion) => {
    setProductInput(suggestion);
    setSuggestions([]);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}
    >
      <main>
        <h1>Get Started</h1>
        <div className="welcome">
          <h2>Welcome to SentiTech</h2>
          <p>Welcome to SentiTech, your intelligent tool for uncovering how people truly feel about tech products across online forums and YouTube videos. Whether you are a business seeking insights to improve products or a consumer looking to do some research on a large purchasing decision, this tool offers various levels of sentiment analysis for a variety of applications.</p>
          <p>When you start to research a product, where do you start? Google and Youtube! This system will allow you to search for a product and automatically aggregate discussions from Google searches about your product, and also similarly collect youtube videos reviewing the product to extract their comments and transcripts - which will all together provide you with meaningful insights into true public sentiment about the product and what people actually think.</p>

          <h2>So Why Is This Important?</h2>
          
          <h3>For consumers:</h3>
          <p>Every year, millions of consumers overspend on tech products due to aggressive marketing strategies and psychological pricing tactics. A study found that over 50% of Gen Z respondents use "buy now, pay later" services, with 29% admitting to overspending because of the system. This trend highlights how impulsive purchasing, often influenced by misleading or overly optimistic reviews, leads to financial strain and buyer’s remorse.</p>
          <p>By aggregating real user sentiment from multiple sources, SentiTech helps users cut through the noise of marketing and advertising, enabling them to make informed decisions based on actual user experiences.</p>
          <p>Past marketing noise, consumers generally lack an efficient way to analyse products holistically on a sentiment level. This tool also aims to save time, providing accessible and quick sentiment analysis on their desired product.</p>
          
          <h3>For companies:</h3>
          <p>For tech companies, understanding consumer sentiment is more than just tracking reviews; it’s about gaining actionable insights to enhance product development, customer experience, and marketing. Companies that effectively analyze customer feedback, like Amazon, refine product features based on sentiment analysis to improve aspects such as durability and usability​</p>
          <p>By incorporating sentiment analysis, SentiTech allows companies to:</p>
          <ol>
            <li>Identify trending concerns (e.g. common complaints about battery life or software issues)</li>
            <li>Adapt marketing strategies to align with customer expectations</li>
            <li>Recognize opportunities for product innovation</li>
          </ol>

          <h2>Before you run your first search...</h2>
          <p>Before you run your first search, please keep in mind that SentiTech provides a prediction of product perception and not definitive purchasing advice or definitive business advice.</p>
          <p>Also note that currently the system works specifically for: Laptops, Smartphones, Headphones, Wearables and Consoles ONLY.</p>
          <p>Using SentiTech for unrelated searches will yield inaccurate and unwanted results.</p>
        </div>

        {/* added loading logic, search is made -> switch to loading container with progress bar instead of spinning circle */}
        {!loading ? (
          <div className="search">
            <h2>Please enter the specific product you would like to analyze:</h2>
            <div className="search-container">
              <input type="text" id="product-input" placeholder="Enter product name..." onChange={(e) => handleInputChange(e.target.value)} value={productInput}/>
              <button id="search-btn" className="green-button" onClick={() => runSearch(productInput)}>
                <span className="material-symbols-outlined" translate="no">search</span>
              </button>
            </div>
            
            {/* trigger on length not availability of suggestions, fixed */}
            {suggestions.length > 0 && (
              <ul className="autocomplete-dropdown">
                {suggestions.map((suggestion, index) => (
                  <li key={index} onClick={() => handleSuggestionClick(suggestion)}>{suggestion}</li>
                ))}
              </ul>
            )}
          </div>    
        ) : (
          <div className="loading-container">
            <div className="progress-bar-background">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p>Processing your request... {progress}% complete</p>
          </div>
        )}
      </main>
    </motion.div>
  );
}

export default GetStarted;