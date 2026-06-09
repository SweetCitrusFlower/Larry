import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { AutopilotProvider } from './context/AutopilotContext.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AutopilotProvider>
        <App />
      </AutopilotProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
