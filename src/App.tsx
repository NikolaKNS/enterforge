import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import PlanWizard from './pages/PlanWizard';
import Result from './pages/Result';

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/plan" element={<PlanWizard />} />
        <Route path="/result/:id" element={<Result />} />
      </Routes>
    </div>
  );
}

export default App;
