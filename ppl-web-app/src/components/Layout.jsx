import React from 'react';
import Header from './Header';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Database, Search, Activity } from 'lucide-react';
import styles from './Layout.module.css';

const Layout = ({ children }) => {
    return (
        <div className={styles.layout}>
            <Header />
            <div className={styles.body}>
                <aside className={styles.sidebar}>
                    <nav className={styles.sidebarNav}>
                        <NavLink
                            to="/new-variable"
                            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
                        >
                            <LayoutDashboard size={20} />
                            <span>Variables</span>
                        </NavLink>
                        <NavLink
                            to="/model-search"
                            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
                        >
                            <Search size={20} />
                            <span>Model Search</span>
                        </NavLink>
                        <NavLink
                            to="/monitoring"
                            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
                        >
                            <Activity size={20} />
                            <span>Monitoring</span>
                        </NavLink>
                    </nav>
                </aside>
                <main className={styles.content}>
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
