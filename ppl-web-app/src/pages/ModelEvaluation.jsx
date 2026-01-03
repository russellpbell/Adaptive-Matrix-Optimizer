import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import styles from './ModelEvaluation.module.css';

const ModelEvaluation = () => {
    const { id } = useParams();
    const [model, setModel] = useState(null);
    const [visualizations, setVisualizations] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [modelRes, vizRes] = await Promise.all([
                    api.get(`/models/${id}`),
                    api.get(`/models/${id}/visualizations`)
                ]);
                setModel(modelRes.data);
                setVisualizations(vizRes.data);
            } catch (err) {
                console.error("Error fetching model details", err);
                // Mock fallback
                setModel({
                    id: id,
                    name: "Model Alpha",
                    description: "Prediction model for Reactor 1",
                    input_variables: ["XMEAS(1)", "XMEAS(2)"],
                    output_variables: ["XMEAS(10)"],
                    metrics: { mse: 0.023, loss: 0.015 }
                });
                setVisualizations({
                    error_dist: "https://via.placeholder.com/600x300?text=Error+Distribution+Placeholder",
                    lime_plot: "https://via.placeholder.com/600x300?text=LIME+Plot+Placeholder"
                });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    if (loading) return <div>Loading...</div>;
    if (!model) return <div>Model not found</div>;

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div>
                    <h1>{model.name}</h1>
                    <p className={styles.subtitle}>{model.description}</p>
                </div>
                <div className={styles.badges}>
                    <span className={styles.badge}>MSE: {model.metrics.mse}</span>
                    <span className={styles.badge}>Loss: {model.metrics.loss}</span>
                </div>
            </header>

            <section className={styles.section}>
                <h2>Model Inputs & Outputs</h2>
                <div className={styles.grid}>
                    <div className={styles.card}>
                        <h3>Inputs</h3>
                        <ul className={styles.list}>
                            {model.input_variables.map((v, i) => <li key={i}>{v}</li>)}
                        </ul>
                    </div>
                    <div className={styles.card}>
                        <h3>Outputs</h3>
                        <ul className={styles.list}>
                            {model.output_variables.map((v, i) => <li key={i}>{v}</li>)}
                        </ul>
                    </div>
                </div>
            </section>

            <section className={styles.section}>
                <h2>Interactive Error Analysis</h2>
                <p className={styles.description}>
                    Select a range of errors in the histogram to see the distribution of input features for those specific samples.
                </p>
                <div className={styles.vizContainer}>
                    {/* Placeholder for Plotly Chart */}
                    <img src={visualizations?.error_dist} alt="Error Distribution" className={styles.vizImage} />
                </div>
            </section>

            <section className={styles.section}>
                <h2>Feature Importance (LIME)</h2>
                <div className={styles.vizContainer}>
                    {/* Placeholder for LIME Chart */}
                    <img src={visualizations?.lime_plot} alt="LIME Analysis" className={styles.vizImage} />
                </div>
            </section>
        </div>
    );
};

export default ModelEvaluation;
