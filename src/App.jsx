

import { useState } from 'react';
import './App.css';

const CTA_LINK = "https://your-link.com"; // Change to your desired link

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState('upload'); // upload | analyzing | result

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
    setStep('upload');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setStep('analyzing');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('https://tattel-ai-review.onrender.com', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to get response');
      const data = await res.json();
      setResult(data);
      setStep('result');
    } catch (err) {
      setError('Error uploading CV or connecting to backend.');
      setStep('upload');
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>CV Review</h1>
      {step === 'upload' && (
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <input type="file" accept=".pdf,.doc,.docx" onChange={handleFileChange} style={{ marginBottom: '1em', width: '100%' }} />
          <button type="submit" disabled={loading || !file} style={{ width: '100%' }}>
            Upload & Get Score
          </button>
          {error && <p style={{ color: '#ed8523', marginTop: '1em' }}>{error}</p>}
        </form>
      )}

      {step === 'analyzing' && (
        <div className="loading">
          <div className="loader"></div>
          <p style={{ color: 'var(--primary)', fontWeight: 500, fontSize: '1.1em' }}>
            Analyzing your CV...<br />
            Did you know? A well-structured CV can increase your interview chances by 60%!
          </p>
        </div>
      )}

      {step === 'result' && result && (
        <div className="result">
          <h2 style={{ color: 'var(--primary)', fontWeight: 700 }}>Score: {result.score ?? 'N/A'}</h2>
          <h3 style={{ marginTop: '1em', marginBottom: '0.5em' }}>Suggestions:</h3>
          <ul>
            {result.suggestions.map((s, i) => (
              <li key={i} style={{ marginBottom: '0.5em' }}>{s}</li>
            ))}
          </ul>
          <div className="cta">
            <a href={CTA_LINK} target="_blank" rel="noopener noreferrer">
              <button className="cta-btn">Make your CV Industry ready today!</button>
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
