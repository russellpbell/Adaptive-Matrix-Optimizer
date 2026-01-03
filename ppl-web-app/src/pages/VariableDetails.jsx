import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getVariablePrediction } from '../api';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import styles from './VariableDetails.module.css';

const VariableDetails = () => {
    const { tag } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const result = await getVariablePrediction(tag);
                // Transform data for Recharts
                // result[tag] = { actual: [], predicted: [], time_steps: [] }
                if (result[tag]) {
                    const chartData = result[tag].time_steps.map((t, i) => ({
                        time: t,
                        Actual: result[tag].actual[i],
                        Predicted: result[tag].predicted[i]
                    }));
                    setData(chartData);
                } else {
                    setError("No data available for this variable.");
                }
            } catch (err) {
                console.error("Failed to fetch prediction:", err);
                setError("Failed to load prediction data. Variable might not be in the model.");
            } finally {
                setLoading(false);
            }
        };

        if (tag) {
            fetchData();
        }
    }, [tag]);

    return (
        <div className={styles.page}>

            <main className={styles.main}>
                <div className={styles.headerRow}>
                    <h1 className={styles.title}>{tag} Details</h1>
                    <button className={styles.refreshButton} onClick={() => window.location.reload()}>
                        Refresh Prediction
                    </button>
                </div>

                {loading && <div className={styles.loading}>Loading prediction...</div>}

                {error && <div className={styles.error}>{error}</div>}

                {!loading && !error && data && (
                    <div className={styles.chartContainer}>
                        <h2>Prediction vs Actual</h2>
                        <div className={styles.chartWrapper}>
                            <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="time" label={{ value: 'Time Step', position: 'insideBottomRight', offset: -5 }} />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="Actual" stroke="#8884d8" strokeWidth={2} dot={false} />
                                    <Line type="monotone" dataKey="Predicted" stroke="#82ca9d" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div className={styles.stats}>
                            <div className={styles.statCard}>
                                <h3>Latest Actual</h3>
                                <p>{data[data.length - 1].Actual.toFixed(4)}</p>
                            </div>
                            <div className={styles.statCard}>
                                <h3>Latest Predicted</h3>
                                <p>{data[data.length - 1].Predicted.toFixed(4)}</p>
                            </div>
                            <div className={styles.statCard}>
                                <h3>Error</h3>
                                <p>{Math.abs(data[data.length - 1].Actual - data[data.length - 1].Predicted).toFixed(4)}</p>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default VariableDetails;
