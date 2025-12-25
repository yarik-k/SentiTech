import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/comparison-tool.css";
import { motion } from "framer-motion";

const ComparisonTool = () => {
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bestFeaturesMap, setBestFeaturesMap] = useState({});
  // const [highlightedFeature, setHighlightedFeature] = useState("");
  // const [bestProduct, setBestProduct] = useState(null); - highlight "best" chosen product from all based on 
  const navigate = useNavigate();

  const handleRunSentiTech = (productName) => {
    navigate(`/get-started?product=${encodeURIComponent(productName)}`);
  };

  // track tooltip visibility and position to dynamically display for best features
  const [tooltip, setTooltip] = useState({ visible: false, content: "", x: 0, y: 0 });

  function createBestFeaturesMap(bestFeaturesArr) {
    const output = {};
  
    if (!bestFeaturesArr) return output;
  
    for (let i = 0; i < bestFeaturesArr.length; i++) {
      const item = bestFeaturesArr[i];
      const featureKey = item.feature.trim();

      output[featureKey] = {product: item.product ? item.product.trim() : "", reason: item.reason ? item.reason.trim() : ""};
    }
  
    return output;
  }

  useEffect(() => {
    setComparisonData([]);
    
    fetch("http://127.0.0.1:8000/api/results")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.comparison_data && data.best_features) {
          setComparisonData(data.comparison_data);

          const bestMap = createBestFeaturesMap(data.best_features);
          setBestFeaturesMap(bestMap);
        }

        // stop loading in any case, potential expansion on error cases
        setLoading(false);
      })
      .catch((err) => console.error("Error:", err))
  }, []);


  const allFeaturesSet = new Set();
  comparisonData.forEach((prod) => {
    Object.keys(prod).forEach((key) => {
      if (key !== "Product") {
        allFeaturesSet.add(key);
      }
    });
  });

  const allFeatures = Array.from(allFeaturesSet);

  if (!comparisonData)
    return <div>No comparison data found.</div>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
      <main>
        <h1>Comparison Tool</h1>
        <div className="main-box">
          <p> Here you can compare similar products on the market to the one you searched and their specifications. See something you like? You also have the option to run any other chosen product through SentiTech to generate a fresh analysis.</p>
          
          <table className="comparison-table" cellPadding="5">
            <thead>
              <tr>
                <th>Feature</th>
                {comparisonData.map((prod, idx) => (
                  <th key={idx}>{prod.Product || "Unknown Product"}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allFeatures.map((feature, rowIdx) => (
                <tr key={rowIdx}>
                  <td>{feature}</td>
                  {comparisonData.map((prod, colIdx) => {
                    const value = prod[feature] || "N/A";
                    const bestInfo = bestFeaturesMap[feature];
                    const isBest = bestInfo && bestInfo.product.toLowerCase() === (prod.Product || "").toLowerCase();
                    const tooltipReason = isBest ? bestInfo.reason : "";

                    return (
                      <td key={colIdx} className={isBest ? "best-cell" : ""} onMouseEnter={(e) => {
                          if (isBest) {
                            setTooltip({ visible: true, content: tooltipReason, x: e.clientX, y: e.clientY });
                          }
                        }}
                        onMouseLeave={() => setTooltip({ ...tooltip, visible: false })}>
                        {value}
                      </td>
                    );
                  })}
                </tr>
              ))}

              <tr>
                <td style={{ visibility: "hidden" }}>Action</td>
                {comparisonData.map((prod, colIdx) => (
                  <td key={colIdx}>
                    {colIdx === 0 ? (
                      <button disabled className="disabled-btn" style={{ cursor: "default" }}>
                        Current Product
                      </button>
                    ) : (
                      <button className="senti-tech-btn" onClick={() => handleRunSentiTech(prod.Product)}>Run SentiTech</button>
                    )}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>

          {tooltip.visible && (
            <div className="hover-tooltip" style={{ top: tooltip.y + 10, left: tooltip.x + 10 }}>{tooltip.content}</div> // offset for cursor
          )}
        </div>
      </main>
    </motion.div>
  );
};

export default ComparisonTool;
