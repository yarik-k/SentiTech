import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, Outlet, Navigate, useLocation, useNavigate } from "react-router-dom";
import Sidebar from "./components/Sidebar.js";
import GetStarted from "./components/GetStarted.js";
import FeatureSentiment from "./components/FeatureSentiment.js";
import EmotionInsights from "./components/EmotionInsights.js";
import Summarization from "./components/Summarization.js";
import ComparisonTool from "./components/ComparisonTool.js";
import Settings from "./components/Settings.js";
import "./styles/index.css";
import { AnimatePresence } from "framer-motion";

function Layout({ searchCompleted, searchLoading }) {
  return (
    <div className="container">
      <Sidebar searchCompleted={searchCompleted} searchLoading={searchLoading} />
      <main id="main-content">
        <Outlet />
      </main>
    </div>
  );
}

function ForceRedirect() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.pathname !== "/get-started") {
      navigate("/get-started", { replace: true });
    }
  }, []);

  return null;
}

function AnimatedRoutes({searchCompleted, setSearchCompleted, darkMode, highContrast, toggleDarkMode, toggleTextToSpeech, toggleHighContrast, searchLoading, setSearchLoading}) {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">{/* wrapped Framer Motion for all pages to be animated */}
      <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Navigate to="/get-started" replace />} />
          <Route path="/" element={<Layout searchCompleted={searchCompleted} searchLoading={searchLoading}/>}>
          <Route path="get-started" element={<GetStarted setSearchCompleted={setSearchCompleted} searchLoading={searchLoading} setSearchLoading={setSearchLoading}/>} />
          <Route path="feature-sentiment-analysis" element={<FeatureSentiment darkMode={darkMode} highContrast={highContrast} />} />
          <Route path="emotion-insights" element={<EmotionInsights darkMode={darkMode} highContrast={highContrast} />} />
          <Route path="summarization" element={<Summarization />} />
          <Route path="comparison-tool" element={<ComparisonTool />} />
          <Route path="settings" element={<Settings darkMode={darkMode} toggleDarkMode={toggleDarkMode} toggleTextToSpeech={toggleTextToSpeech} toggleHighContrast={toggleHighContrast}/>} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const [searchCompleted, setSearchCompleted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false); // AI ASSISTED text to speech functionality
  const [searchLoading, setSearchLoading] = useState(false); // added to disable Settings while search is loading for nav bugs

  const [darkMode, setDarkMode] = useState(localStorage.getItem("dark-mode") !== "disabled");
  const [textToSpeechEnabled, setTextToSpeechEnabled] = useState(localStorage.getItem("text-to-speech") === "enabled");
  const [highContrast, setHighContrast] = useState(localStorage.getItem("high-contrast") === "enabled");

  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
    localStorage.setItem("dark-mode", darkMode ? "enabled" : "disabled");

    document.body.classList.toggle("high-contrast-mode", highContrast);
    localStorage.setItem("high-contrast", highContrast ? "enabled" : "disabled");
  }, [darkMode, highContrast]);
  
  const speakMainContent = () => {
    const synth = window.speechSynthesis;

    if (synth.speaking) {
      synth.cancel();
      setIsSpeaking(false);
      return;
    }

    const content = document.querySelector("main");
    if (content && window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(content.innerText);
      utterance.rate = 1;
      utterance.pitch = 1;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);

      synth.speak(utterance);
    }
  };

  const toggleDarkMode = () => {
    if(highContrast && darkMode) {
      setHighContrast(false);
    }
    setDarkMode(!darkMode);
  };

  const toggleTextToSpeech = () => {
    setTextToSpeechEnabled((prev) => !prev);
  };

  const toggleHighContrast = () => {
    setHighContrast(!highContrast);
    setDarkMode(true)
  };

  return (
      <Router>
        <ForceRedirect />
        <AnimatedRoutes searchCompleted={searchCompleted} setSearchCompleted={setSearchCompleted} darkMode={darkMode} highContrast={highContrast} toggleDarkMode={toggleDarkMode} toggleTextToSpeech={toggleTextToSpeech} toggleHighContrast={toggleHighContrast} searchLoading={searchLoading} setSearchLoading={setSearchLoading}/>
        {textToSpeechEnabled && (
          <button className="tts-button" onClick={speakMainContent}>
            <span className="material-symbols-outlined" translate="no">{isSpeaking ? "cancel" : "text_to_speech"}</span>
            <p>{isSpeaking ? "Stop" : "Speak"}</p>
          </button>
        )}
      </Router>
  );
}

export default App;
