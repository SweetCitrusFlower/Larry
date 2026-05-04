import React from 'react';

const Navbar = ({ language, setLanguage, onLoginClick }) => {
  const languages = ['python', 'javascript', 'typescript', 'cpp', 'java', 'html', 'css'];

  return (
    <nav className="navbar">
      <div className="nav-left">
        <div className="logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          <span>Larry AI</span>
        </div>
        <div className="lang-selector">
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            {languages.map(lang => (
              <option key={lang} value={lang}>{lang.toUpperCase()}</option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="nav-center">
        <button className="btn-run">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Run
        </button>
      </div>

      <div className="nav-right">
        <button className="btn-login" onClick={onLoginClick}>
          Login
        </button>
        <button className="btn-register">
          Sign Up
        </button>
      </div>

    </nav>
  );
};

export default Navbar;
