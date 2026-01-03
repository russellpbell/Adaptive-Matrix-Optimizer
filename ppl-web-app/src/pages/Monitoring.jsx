import React, { useState } from 'react';
import { Activity, CheckCircle, AlertTriangle } from 'lucide-react';
import styles from './Monitoring.module.css';

const Monitoring = () => {
    // Mock data for controllers
    const [controllers] = useState([
        { id: 'C-101', name: 'Reactor Temp Controller', status: 'Optimal', performance: 98.5, lastUpdate: '2 mins ago' },
        { id: 'C-102', name: 'Distillation Flow', status: 'Warning', performance: 85.2, lastUpdate: '1 min ago' },
        { id: 'C-205', name: 'Feed Pump Pressure', status: 'Optimal', performance: 99.1, lastUpdate: '5 mins ago' },
        { id: 'C-310', name: 'Cooling Water Loop', status: 'Optimal', performance: 97.8, lastUpdate: '30 secs ago' },
    ]);

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1>System Monitoring</h1>
                <div className={styles.stats}>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Active Controllers</span>
                        <span className={styles.statValue}>{controllers.length}</span>
                    </div>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Avg Performance</span>
                        <span className={styles.statValue}>95.1%</span>
                    </div>
                </div>
            </header>

            <div className={styles.grid}>
                {controllers.map(c => (
                    <div key={c.id} className={styles.card}>
                        <div className={styles.cardHeader}>
                            <div className={styles.titleInfo}>
                                <h3>{c.name}</h3>
                                <span className={styles.id}>{c.id}</span>
                            </div>
                            {c.status === 'Optimal' ? (
                                <CheckCircle className={styles.iconSuccess} size={20} />
                            ) : (
                                <AlertTriangle className={styles.iconWarning} size={20} />
                            )}
                        </div>

                        <div className={styles.cardBody}>
                            <div className={styles.metricRow}>
                                <span>Status</span>
                                <span className={`${styles.statusBadge} ${styles[c.status.toLowerCase()]}`}>
                                    {c.status}
                                </span>
                            </div>
                            <div className={styles.metricRow}>
                                <span>Performance</span>
                                <div className={styles.progressBar}>
                                    <div
                                        className={styles.progressFill}
                                        style={{ width: `${c.performance}%`, backgroundColor: c.status === 'Optimal' ? '#10b981' : '#f59e0b' }}
                                    ></div>
                                </div>
                                <span className={styles.perfValue}>{c.performance}%</span>
                            </div>
                        </div>

                        <div className={styles.cardFooter}>
                            <span>Updated {c.lastUpdate}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Monitoring;
