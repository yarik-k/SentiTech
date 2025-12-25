import React from "react";
import "../styles/index.css";
import "../styles/settings.css";
import { motion } from "framer-motion";

const Settings = ({ darkMode, toggleDarkMode, toggleTextToSpeech, toggleHighContrast }) => {
  
  const runTranslation = (langCode) => {
    // hacky and not ideal google translate method, would be better to translate targeted elements as this may fail
    const select = document.querySelector('.goog-te-combo');
    if (select) {
      select.value = langCode;
      select.dispatchEvent(new Event('change'));
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
      <main>
        <h1>Settings</h1>
        <div className="main-box">
          <div className="toggle-dark">
            <h2>Toggle Dark/Light Mode:</h2>
            <button id="dark-mode-toggle" onClick={toggleDarkMode}>
              <span className="material-symbols-outlined" translate="no">
                {darkMode ? "light_mode" : "dark_mode"}
              </span>
            </button>
          </div>
          <div className="toggle-speech">
            <h2>Toggle Text-to-Speech:</h2>
            <button onClick={toggleTextToSpeech}>
              <span className="material-symbols-outlined" translate="no">text_to_speech</span>
            </button>
          </div>
          <div className="toggle-contrast">
            <h2>Toggle High-Contrast:</h2>
            <button onClick={toggleHighContrast}>
              <span className="material-symbols-outlined" translate="no">contrast</span>
            </button>
          </div>
          <h2>Language Selection:</h2>
          <div className="language-picker">
          <button onClick={() => runTranslation('en')}>
            <img src="https://flagcdn.com/w80/gb.png" alt="English" />
          </button>
          <button onClick={() => runTranslation('es')}>
            <img src="https://flagcdn.com/w80/es.png" alt="Spanish" />
          </button>
          <button onClick={() => runTranslation('zh-CN')}>
            <img src="https://flagcdn.com/w80/cn.png" alt="Chinese" />
          </button>
          <button onClick={() => runTranslation('ru')}>
            <img src="https://flagcdn.com/w80/ru.png" alt="Russian" />
          </button>
          <button onClick={() => runTranslation('ar')}>
            <img src="https://flagcdn.com/w80/sa.png" alt="Arabic" />
          </button>
          <button onClick={() => runTranslation('fr')}>
            <img src="https://flagcdn.com/w80/fr.png" alt="French" />
          </button>
          {/* add dropdown for a wide selection of languages
          <button onClick={() => runTranslation('de')}>
            <img src="https://flagcdn.com/w80/de.png" alt="German" />
          </button>
          <button onClick={() => runTranslation('hi')}>
            <img src="https://flagcdn.com/w80/in.png" alt="Hindi" />
          </button>
          <button onClick={() => runTranslation('ja')}>
            <img src="https://flagcdn.com/w80/jp.png" alt="Japanese" />
          </button>
          <button onClick={() => runTranslation('ko')}>
            <img src="https://flagcdn.com/w80/kr.png" alt="Korean" />
          </button>
          <button onClick={() => runTranslation('it')}>
            <img src="https://flagcdn.com/w80/it.png" alt="Italian" />
          </button>
          */}
          </div>
        </div>
      </main>
    </motion.div>
  );
};
export default Settings