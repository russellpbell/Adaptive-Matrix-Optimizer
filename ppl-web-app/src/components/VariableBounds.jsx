import React from 'react';
import styles from './VariableBounds.module.css';

const VariableBounds = ({ bounds, onChange }) => {
    const handleChange = (field, value) => {
        onChange({ ...bounds, [field]: value });
    };

    // Validation checks
    const isHighInvalid = bounds.High && bounds.HiHi && parseFloat(bounds.High) > parseFloat(bounds.HiHi);
    const isLowInvalid = bounds.Low && bounds.LoLo && parseFloat(bounds.Low) < parseFloat(bounds.LoLo);

    return (
        <div className={styles.container}>
            <h3 className={styles.title}>Variable Bounds</h3>

            <div className={styles.grid}>
                {/* HiHi */}
                <div className={styles.row}>
                    <label className={styles.label}>HiHi</label>
                    <div className={`${styles.inputWrapper} ${styles.redBg}`}>
                        <input
                            type="number"
                            placeholder="Value"
                            className={styles.input}
                            value={bounds.HiHi}
                            onChange={(e) => handleChange('HiHi', e.target.value)}
                        />
                    </div>
                </div>

                {/* High */}
                <div className={styles.row}>
                    <label className={styles.label}>High</label>
                    <div className={`${styles.inputWrapper} ${styles.yellowBg} ${isHighInvalid ? styles.error : ''}`}>
                        <input
                            type="number"
                            placeholder="Value"
                            className={styles.input}
                            value={bounds.High}
                            onChange={(e) => handleChange('High', e.target.value)}
                        />
                    </div>
                </div>
                {isHighInvalid && <div className={styles.errorMsg}>High must be &lt; HiHi</div>}

                {/* Objective */}
                <div className={styles.row}>
                    <label className={styles.label}>Objective</label>
                    <div className={`${styles.inputWrapper} ${styles.greenBg}`}>
                        <input
                            type="text"
                            placeholder="Max / Min / Target Value"
                            className={styles.input}
                            value={bounds.Objective}
                            onChange={(e) => handleChange('Objective', e.target.value)}
                        />
                    </div>
                </div>

                {/* Low */}
                <div className={styles.row}>
                    <label className={styles.label}>Low</label>
                    <div className={`${styles.inputWrapper} ${styles.yellowBg} ${isLowInvalid ? styles.error : ''}`}>
                        <input
                            type="number"
                            placeholder="Value"
                            className={styles.input}
                            value={bounds.Low}
                            onChange={(e) => handleChange('Low', e.target.value)}
                        />
                    </div>
                </div>
                {isLowInvalid && <div className={styles.errorMsg}>Low must be &gt; LoLo</div>}

                {/* LoLo */}
                <div className={styles.row}>
                    <label className={styles.label}>LoLo</label>
                    <div className={`${styles.inputWrapper} ${styles.redBg}`}>
                        <input
                            type="number"
                            placeholder="Value"
                            className={styles.input}
                            value={bounds.LoLo}
                            onChange={(e) => handleChange('LoLo', e.target.value)}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default VariableBounds;
