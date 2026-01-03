import React, { useState } from 'react';
import { createVariable } from '../api';

import TagSelector from '../components/TagSelector';
import LocationInputs from '../components/LocationInputs';
import VariableBounds from '../components/VariableBounds';
import MultiSelect from '../components/MultiSelect';
import styles from './NewVariable.module.css';

const MOCK_TAGS = [
    "TI-101", "FIC-204", "PI-12345", "TI-23456", "PI-34567",
    "T-1001 RR", "Ethylene Product", "Benzene Product", "C-1001",
    "P-1002", "P-2001", "C-1002", "LI-505", "FI-602",
    "TI-701", "PI-808", "AI-909", "XV-111", "ZS-222", "HS-333"
];

const NewVariable = () => {
    const [tag, setTag] = useState('');
    const [location, setLocation] = useState('');
    const [excelData, setExcelData] = useState({ filePath: '', cellLocation: '' });
    const [bounds, setBounds] = useState({ HiHi: '', High: '', Objective: '', Low: '', LoLo: '' });

    // Other fields
    const [unitSubsection, setUnitSubsection] = useState([]);
    const [forecastType, setForecastType] = useState('');
    const [keyWords, setKeyWords] = useState([]);
    const [forecastVariables, setForecastVariables] = useState([]);

    const handleSave = async () => {
        try {
            // Prepare data for backend (convert empty strings to null/float)
            const payload = {
                tag,
                location,
                excel_data: location === 'Excel' ? excelData : null,
                hihi: bounds.HiHi ? parseFloat(bounds.HiHi) : null,
                high: bounds.High ? parseFloat(bounds.High) : null,
                objective: bounds.Objective ? parseFloat(bounds.Objective) : null,
                low: bounds.Low ? parseFloat(bounds.Low) : null,
                lolo: bounds.LoLo ? parseFloat(bounds.LoLo) : null,
                unit_subsection: unitSubsection,
                forecast_type: forecastType || null,
                key_words: keyWords,
                forecast_variables: forecastVariables
            };

            console.log('Sending payload:', payload);
            await createVariable(payload);
            alert('Variable Saved Successfully!');

            // Optional: Reset form or redirect
        } catch (err) {
            console.error('Failed to save variable:', err);
            const errorMessage = err.response?.data?.detail || 'Failed to save variable.';
            alert(`Error: ${errorMessage}`);
        }
    };

    // Determine button text
    const isTrainingEnabled = forecastType && forecastVariables.length > 0;
    const buttonText = isTrainingEnabled ? "Save & Train" : "Save";

    return (
        <div className={styles.page}>


            <main className={styles.main}>
                <h1 className={styles.title}>New Variable</h1>

                <TagSelector value={tag} onChange={setTag} />

                <LocationInputs
                    location={location}
                    onLocationChange={setLocation}
                    excelData={excelData}
                    onExcelDataChange={setExcelData}
                />

                <div className={styles.gridContainer}>
                    {/* Left Column */}
                    <div className={styles.leftColumn}>
                        <VariableBounds bounds={bounds} onChange={setBounds} />
                    </div>

                    {/* Right Column */}
                    <div className={styles.rightColumn}>

                        {/* Unit Subsection */}
                        <div className={styles.field}>
                            <label className={styles.label}>Unit Subsection</label>
                            <MultiSelect
                                value={unitSubsection}
                                onChange={setUnitSubsection}
                                placeholder="Add subsection..."
                            />
                        </div>

                        {/* Key Words (Moved Up) */}
                        <div className={styles.field}>
                            <label className={styles.label}>Key Words</label>
                            <MultiSelect
                                value={keyWords}
                                onChange={setKeyWords}
                                placeholder="Add keywords..."
                            />
                        </div>

                        {/* Forecast Type */}
                        <div className={styles.field}>
                            <label className={styles.label}>Forecast Type <span className={styles.italic}>(discrete or continuous)</span></label>
                            <div className={styles.selectWrapper}>
                                <select
                                    className={styles.select}
                                    value={forecastType}
                                    onChange={(e) => setForecastType(e.target.value)}
                                >
                                    <option value="">Select Type...</option>
                                    <option value="Discrete">Discrete</option>
                                    <option value="Continuous">Continuous</option>
                                </select>
                                <span className={styles.arrow}>▼</span>
                            </div>
                        </div>

                        {/* Forecast Variables (Restricted) */}
                        <div className={styles.field}>
                            <label className={styles.label}>Forecast Variables <span className={styles.italic}>(select from existing)</span></label>
                            <MultiSelect
                                value={forecastVariables}
                                onChange={setForecastVariables}
                                placeholder="Select variables..."
                                options={MOCK_TAGS}
                                restrictToOptions={true}
                            />
                        </div>

                    </div>
                </div>

                <div className={styles.footer}>
                    <button className={styles.saveButton} onClick={handleSave}>
                        {buttonText}
                    </button>
                </div>

            </main>
        </div>
    );
};

export default NewVariable;
