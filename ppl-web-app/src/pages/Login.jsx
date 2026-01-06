import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserContext } from '../context/UserContext';
import { Globe, ArrowRight, Loader2 } from 'lucide-react';

const Login = () => {
    const [loading, setLoading] = useState(false);
    const { login } = useContext(UserContext);
    const navigate = useNavigate();

    const handleContinue = () => {
        setLoading(true);
        // Simulate a brief loading state for better UX
        setTimeout(() => {
            login('dummy_token_dev_mode');
            navigate('/model-search');
        }, 800);
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-[#0f1115] font-sans relative overflow-hidden">
            {/* Background Ambient Glow */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 rounded-full blur-[120px]" />

            <div className="w-full max-w-md bg-white/5 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-white/10 relative z-10 flex flex-col items-center placeholder-content-center">

                {/* Header */}
                <div className="text-center mb-10">
                    <div className="flex items-center justify-center mb-6">
                        <div className="p-4 bg-blue-600/20 rounded-2xl border border-blue-500/30 shadow-inner shadow-blue-500/20">
                            <Globe className="w-10 h-10 text-blue-400" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
                        Adaptive Matrix Optimizer
                    </h1>
                    <p className="text-gray-400 text-base max-w-[280px] mx-auto leading-relaxed">
                        Next-Generation Open-Loop Optimizer for Industrial Systems
                    </p>
                </div>

                {/* Simple Entry */}
                <div className="w-full space-y-6">
                    <button
                        onClick={handleContinue}
                        disabled={loading}
                        className="w-full flex items-center justify-center py-4 px-6 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0f1115] focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-900/40 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        {loading ? (
                            <Loader2 className="w-6 h-6 animate-spin" />
                        ) : (
                            <>
                                <span>Continue to App</span>
                                <ArrowRight className="w-5 h-5 ml-2" />
                            </>
                        )}
                    </button>

                    <div className="text-center space-y-2">
                        <p className="text-xs text-gray-500 uppercase tracking-widest font-medium">
                            Development Build
                        </p>
                        <p className="text-[10px] text-gray-600">
                            Authentication bypassed for testing
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
