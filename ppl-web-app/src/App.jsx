import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Subscription from './pages/Subscription';
import NewVariable from './pages/NewVariable';
import VariableDetails from './pages/VariableDetails';
import AccountSettings from './pages/AccountSettings';
import Monitoring from './pages/Monitoring';
import ModelSearch from './pages/ModelSearch';
import ModelEvaluation from './pages/ModelEvaluation';
import Layout from './components/Layout';
import { UserProvider, UserContext } from './context/UserContext';

const RequireAuth = ({ children }) => {
  const { user, loading } = useContext(UserContext);
  const location = useLocation();

  if (loading) {
    return <div className="text-white text-center mt-10">Loading...</div>; // Simple loading state
  }

  if (!user) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return children;
};

function App() {
  return (
    <UserProvider>
      <Router>
        <div className="app-container">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes with Layout */}
            <Route path="/new-variable" element={<RequireAuth><Layout><NewVariable /></Layout></RequireAuth>} />
            <Route path="/variable/:tag" element={<RequireAuth><Layout><VariableDetails /></Layout></RequireAuth>} />
            <Route path="/settings" element={<RequireAuth><Layout><AccountSettings /></Layout></RequireAuth>} />
            <Route path="/monitoring" element={<RequireAuth><Layout><Monitoring /></Layout></RequireAuth>} />
            <Route path="/model-search" element={<RequireAuth><Layout><ModelSearch /></Layout></RequireAuth>} />
            <Route path="/models/:id" element={<RequireAuth><Layout><ModelEvaluation /></Layout></RequireAuth>} />

            {/* Subscription Route (Wrapped in Layout or Standalone? Let's keep it standalone for now or Layout) */}
            <Route path="/subscription" element={<RequireAuth><Layout><Subscription /></Layout></RequireAuth>} />
          </Routes>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
