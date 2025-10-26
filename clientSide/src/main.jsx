import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// StrictMode deshabilitado para evitar dobles llamadas en desarrollo
// En producción esto no afecta, pero en dev causa que los efectos se ejecuten 2 veces
ReactDOM.createRoot(document.getElementById('root')).render(
  <App />
)

