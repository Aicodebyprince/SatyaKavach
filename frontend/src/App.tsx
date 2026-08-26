import { useState, createContext, useContext } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Footer from './components/Footer';
import type { Language } from './i18n/translations';

// Language context
export const LangContext = createContext<{
  lang: Language;
  setLang: (l: Language) => void;
}>({ lang: 'hi', setLang: () => {} });

export const useLang = () => useContext(LangContext);

function App() {
  const [lang, setLang] = useState<Language>(() => {
    // Allow forcing language via URL (?lang=en|hi) — handy for demos & screenshots
    const param = new URLSearchParams(window.location.search).get('lang');
    if (param === 'en' || param === 'hi') return param;
    return (localStorage.getItem('satyakavach_lang') as Language) || 'hi';
  });

  const handleSetLang = (l: Language) => {
    setLang(l);
    localStorage.setItem('satyakavach_lang', l);
  };

  return (
    <LangContext.Provider value={{ lang, setLang: handleSetLang }}>
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-[560px] w-[900px] -translate-x-1/2 rounded-full bg-saffron-500/[0.07] blur-[140px]" />
        <div className="absolute right-[-180px] top-1/3 h-[420px] w-[420px] rounded-full bg-violet-600/[0.06] blur-[120px]" />
        <div className="absolute bottom-[-160px] left-[-120px] h-[380px] w-[380px] rounded-full bg-cyan-500/[0.04] blur-[120px]" />
      </div>

      <div className="flex min-h-screen flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/result/:mediaId" element={<ResultsPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </LangContext.Provider>
  );
}

export default App;
