import React from 'react';
import styles from './LocationInputs.module.css';

const LocationInputs = ({ location, onLocationChange, excelData, onExcelDataChange }) => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.row}>
                {/* Variable Location */}
                <div className={styles.field}>
                    <label className={styles.label}>Variable Location</label>
                    <div className={styles.selectWrapper}>
                        <select
                            className={styles.select}
                            value={location}
                            onChange={(e) => onLocationChange(e.target.value)}
                        >
                            <option value="">Select Location...</option>
                            <option value="Historian">Historian</option>
                            <option value="Database">Database</option>
                            <option value="Excel">Excel</option>
                        </select>
                        <span className={styles.arrow}>▼</span>
                    </div>
                </div>

                {/* Conditional Excel Inputs */}
                {location === 'Excel' && (
                    <>
                        <div className={styles.field}>
                            <label className={styles.label}>If Excel, select file path</label>
                            <div className={styles.inputWrapper}>
                                <input
                                    type="file"
                                    className={styles.fileInput}
                                    onChange={(e) => onExcelDataChange({ ...excelData, filePath: e.target.files[0]?.name || '' })}
                                />
                            </div>
                        </div>

                        <div className={styles.field}>
                            <label className={styles.label}>If Excel, define cell location</label>
                            <div className={styles.inputWrapper}>
                                <input
                                    type="text"
                                    className={styles.input}
                                    value={excelData.cellLocation}
                                    onChange={(e) => onExcelDataChange({ ...excelData, cellLocation: e.target.value })}
                                />
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default LocationInputs;
