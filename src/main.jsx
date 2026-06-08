import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'
import './index.css'
import { RouteCompo } from './components/RouteCompo.jsx'
import {RouterProvider} from 'react-router-dom'
import { AuthProvider } from './components/AuthContext.jsx'


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
    <RouterProvider router={RouteCompo}/>
    </AuthProvider>
    
  </StrictMode>,
)
