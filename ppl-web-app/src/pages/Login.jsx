import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserContext } from '../context/UserContext';
import * as loginApi from '../api';
import { Globe, ArrowRight, Mail, Lock, AlertCircle, Loader2 } from 'lucide-react';

const Login = () => {
    const [step, setStep] = useState(1); // 1: Email, 2: Code
    const [email, setEmail] = useState('');
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [countdown, setCountdown] = useState(0);

    const { login } = useContext(UserContext);
    const navigate = useNavigate();

    // Reset error when typing
    useEffect(() => {
        if (error) setError('');
    }, [email, code]);

    // Countdown timer for resend
    useEffect(() => {
        if (countdown > 0) {
            const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [countdown]);

    const handleRequestCode = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await loginApi.requestCode(email);
            setStep(2);
            setCountdown(30); // 30s cooldown before resend
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to send verification code. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyCode = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const data = await loginApi.verifyCode(email, code);
            login(data.access_token);
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid or expired code. Please check and try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleResendCode = async () => {
        if (countdown > 0) return;
        setLoading(true);
        try {
            await loginApi.requestCode(email);
            setCountdown(30);
            setError('');
        } catch (err) {
            setError('Failed to resend code.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-[#0f1115] font-sans relative overflow-hidden">
            {/* Background Ambient Glow */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 rounded-full blur-[120px]" />

            <div className="w-full max-w-md bg-white/5 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-white/10 relative z-10">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-4">
                        <div className="p-3 bg-blue-600/20 rounded-xl border border-blue-500/30">
                            <Globe className="w-8 h-8 text-blue-400" />
                        </div>
                    </div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">
                        Adaptive Matrix Optimizer
                    </h1>
                    <p className="text-gray-400 text-sm mt-2">
                        {step === 1
                            ? "Sign in to access your workspace"
                            : "A secure verification code has been sent"}
                    </p>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="mb-6 flex items-start p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{error}</span>
                    </div>
                )}

                {/* Simple Entry */}
                <div className="space-y-6">
                    <button
                        onClick={() => {
                            setLoading(true);
                            // Simulate a brief loading state for better UX
                            setTimeout(() => {
                                login('dummy_token_dev_mode');
                                navigate('/model-search');
                            }, 800);
                        }}
                        disabled={loading}
                        className="w-full flex items-center justify-center py-3 px-4 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0f1115] focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-900/20"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <span>Continue to App</span>
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </>
                        )}
                    </button>

                    <p className="text-center text-xs text-gray-500">
                        Development Mode Enabled
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
