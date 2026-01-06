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

            {/* Protected Routes with Layout - Auth bypassed */}
            <Route path="/new-variable" element={<Layout><NewVariable /></Layout>} />
            <Route path="/variable/:tag" element={<Layout><VariableDetails /></Layout>} />
            <Route path="/settings" element={<Layout><AccountSettings /></Layout>} />
            <Route path="/monitoring" element={<Layout><Monitoring /></Layout>} />
            <Route path="/model-search" element={<Layout><ModelSearch /></Layout>} />
            <Route path="/models/:id" element={<Layout><ModelEvaluation /></Layout>} />

            {/* Subscription Route */}
            <Route path="/subscription" element={<Layout><Subscription /></Layout>} />
          </Routes>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
