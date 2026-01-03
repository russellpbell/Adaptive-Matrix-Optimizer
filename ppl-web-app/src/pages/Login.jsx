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
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 font-sans">
            <div className="w-full max-w-md bg-white p-8 rounded-xl shadow-sm border border-gray-100">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-4">
                        <Globe className="w-8 h-8 text-blue-500" />
                        <h1 className="ml-3 text-xl font-semibold text-gray-900">
                            Adaptive Matrix Optimizer
                        </h1>
                    </div>

                    <p className="text-gray-500 text-sm">
                        {step === 1
                            ? "Sign in with your email"
                            : "A secure verification code has been sent."}
                    </p>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="mb-6 flex items-start p-4 rounded-lg bg-red-50 text-red-600 text-sm">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{error}</span>
                    </div>
                )}

                {/* Authentication Forms */}
                {step === 1 ? (
                    <form onSubmit={handleRequestCode} className="space-y-6">
                        <div className="space-y-2">
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                Email
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className="block w-full px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors sm:text-sm"
                                placeholder=""
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                "Log in / Sign up"
                            )}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyCode} className="space-y-6">
                        <div className="space-y-2">
                            <label htmlFor="code" className="block text-sm font-medium text-gray-700">
                                Verification Code
                            </label>
                            <input
                                id="code"
                                name="code"
                                type="text"
                                autoComplete="one-time-code"
                                required
                                maxLength={6}
                                className="block w-full px-4 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-center font-mono text-lg tracking-[0.25em]"
                                placeholder="······"
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                        >
                            {loading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                'Secure Login'
                            )}
                        </button>

                        <div className="flex items-center justify-between text-sm pt-2">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="text-gray-500 hover:text-gray-900 transition-colors"
                            >
                                ← Change email
                            </button>
                            <button
                                type="button"
                                onClick={handleResendCode}
                                disabled={countdown > 0 || loading}
                                className={`${countdown > 0 ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-700 font-medium'} transition-colors`}
                            >
                                {countdown > 0 ? `Resend (${countdown}s)` : 'Resend code'}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default Login;
