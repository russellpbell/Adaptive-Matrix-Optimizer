import React, { useState, useEffect } from 'react';
import { Search, Plus, BarChart2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import api, { uploadModel, getModels } from '../api';
// Use existing or create new CSS module. For now, inline or reuse common styles might be easier, 
// but I'll create a dedicated module for cleanliness.
import styles from './ModelSearch.module.css';

const ModelSearch = () => {
    const [models, setModels] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        // Fetch models from API
        const fetchModels = async () => {
            try {
                // Assuming api.getModels() exists or direct call
                const response = await api.get('/models/');
                setModels(response.data);
            } catch (error) {
                console.error("Failed to fetch models", error);
                // Mock data if API fails or backend not fully ready
                setModels([
                    { id: "model_1", name: "Reactor Temp Control", status: "Ready", accuracy: 0.95 },
                    { id: "model_2", name: "Distillation Column A", status: "Training", accuracy: 0.0 }
                ]);
            }
        };
        fetchModels();
    }, []);

    const filteredModels = models.filter(m =>
        m.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>Model Registry</h1>
                <div className="flex gap-3">
                    <input
                        type="file"
                        id="zip-upload"
                        accept=".zip"
                        style={{ display: 'none' }}
                        onChange={async (e) => {
                            if (e.target.files && e.target.files[0]) {
                                try {
                                    alert("Uploading model... this may take a moment."); // Simple feedback
                                    await uploadModel(e.target.files[0]);
                                    alert("Model uploaded successfully!");
                                    // Refresh models
                                    const data = await getModels();
                                    setModels(data);
                                } catch (err) {
                                    console.error(err);
                                    alert("Failed to upload model.");
                                }
                            }
                        }}
                    />
                    <button
                        onClick={() => document.getElementById('zip-upload').click()}
                        className={`${styles.createButton} bg-green-600 hover:bg-green-700`}
                    >
                        <Plus size={16} />
                        <span>Upload .zip</span>
                    </button>
                    <Link to="/new-variable" className={styles.createButton}>
                        <Plus size={16} />
                        <span>Train New Model</span>
                    </Link>
                </div>
            </div>

            <div className={styles.searchBar}>
                <Search className={styles.searchIcon} size={20} />
                <input
                    type="text"
                    placeholder="Search models..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className={styles.searchInput}
                />
            </div>

            <div className={styles.grid}>
                {filteredModels.map(model => (
                    <div key={model.id} className={styles.card}>
                        <div className={styles.cardHeader}>
                            <h3>{model.name}</h3>
                            <span className={`${styles.status} ${styles[model.status.toLowerCase()]}`}>
                                {model.status}
                            </span>
                        </div>
                        <div className={styles.cardBody}>
                            <div className={styles.metric}>
                                <span className={styles.label}>Accuracy</span>
                                <span className={styles.value}>{(model.accuracy * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                        <div className={styles.cardFooter}>
                            <Link to={`/models/${model.id}`} className={styles.linkButton}>
                                <BarChart2 size={16} />
                                Evaluate
                            </Link>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ModelSearch;
