import React, { useState } from 'react';
import { createCheckoutSession } from '../api';

const Subscription = () => {
    const [loading, setLoading] = useState(false);
    const [plan, setPlan] = useState('month'); // 'month' or 'year'

    // Check for success/cancel query params
    const query = new URLSearchParams(window.location.search);
    const success = query.get('success');
    const canceled = query.get('canceled');

    const handleSubscribe = async () => {
        setLoading(true);
        try {
            const data = await createCheckoutSession(plan);
            // Redirect to Stripe Checkout
            window.location.href = data.url;
        } catch (error) {
            console.error(error);
            alert("Failed to initiate subscription. Please try again.");
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
                <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center max-w-lg">
                    <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <h2 className="text-3xl font-bold mb-4 text-green-400">Subscription Successful!</h2>
                    <p className="text-gray-300 mb-6">Thank you for subscribing to PPL Premium. Your account has been upgraded.</p>
                    <a href="/" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition duration-200">
                        Go to Dashboard
                    </a>
                </div>
            </div>
        );
    }

    if (canceled) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
                <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center max-w-lg">
                    <svg className="w-16 h-16 text-yellow-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    <h2 className="text-3xl font-bold mb-4 text-yellow-400">Subscription Canceled</h2>
                    <p className="text-gray-300 mb-6">You canceled the checkout process. If you change your mind, you can try again.</p>
                    <a href="/subscription" className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded transition duration-200">
                        Try Again
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
            <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                Unlock PPL Premium
            </h1>

            <div className="bg-gray-800 rounded-xl shadow-2xl overflow-hidden max-w-md w-full border border-gray-700">
                <div className="p-8">
                    {/* Toggle */}
                    <div className="flex justify-center mb-6">
                        <div className="bg-gray-700 p-1 rounded-lg flex">
                            <button
                                onClick={() => setPlan('month')}
                                className={`px-4 py-2 rounded-md text-sm font-medium transition ${plan === 'month' ? 'bg-blue-600 text-white shadow' : 'text-gray-300 hover:text-white'}`}
                            >
                                Monthly
                            </button>
                            <button
                                onClick={() => setPlan('year')}
                                className={`px-4 py-2 rounded-md text-sm font-medium transition ${plan === 'year' ? 'bg-blue-600 text-white shadow' : 'text-gray-300 hover:text-white'}`}
                            >
                                Yearly
                            </button>
                        </div>
                    </div>

                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-semibold text-white">Pro Plan</h2>
                        <div>
                            <span className="text-3xl font-bold text-blue-400">
                                {plan === 'month' ? '$99' : '$999'}
                            </span>
                            <span className="text-base text-gray-400 font-normal">
                                {plan === 'month' ? '/mo' : '/yr'}
                            </span>
                        </div>
                    </div>

                    <ul className="mb-8 space-y-4">
                        <li className="flex items-center text-gray-300">
                            <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Unlimited Model Training
                        </li>
                        <li className="flex items-center text-gray-300">
                            <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Advanced Analytics
                        </li>
                        <li className="flex items-center text-gray-300">
                            <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            Priority Support
                        </li>
                    </ul>

                    <button
                        onClick={handleSubscribe}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-3 rounded-lg shadow-lg transform transition hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Processing...' : 'Subscribe Now'}
                    </button>
                    <p className="mt-4 text-xs text-center text-gray-500">Secure payment via Polar</p>
                </div>
            </div>
        </div>
    );
};

export default Subscription;
