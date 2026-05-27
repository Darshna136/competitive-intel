import { BrowserRouter, Routes, Route } from 'react-router-dom'
import WarRoom from './pages/WarRoom'
import CompetitorDetail from './pages/CompetitorDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WarRoom />} />
        <Route path="/competitor/:name" element={<CompetitorDetail />} />
      </Routes>
    </BrowserRouter>
  )
}