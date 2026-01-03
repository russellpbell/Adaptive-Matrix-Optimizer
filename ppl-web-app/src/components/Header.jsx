import React, { useState } from 'react';
import { Home, Search, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './Header.module.css';
import { useUser } from '../context/UserContext';

const Header = () => {
    const { user, logout } = useUser();
    const [showDropdown, setShowDropdown] = useState(false);
    const navigate = useNavigate();
    const defaultAvatar = "https://i.pravatar.cc/150?img=5";

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className={styles.header}>
            <div className={styles.leftSection}>
                <Link to="/new-variable" className={styles.homeButton}>
                    <Home size={20} />
                </Link>
            </div>

            <div className={styles.centerSection}>
                <nav className={styles.nav}>
                    <a href="#" className={`${styles.navLink} ${styles.active}`}>Predictive Operations Suite</a>
                    <a href="#" className={styles.navLink}>Predictive Performance Suite</a>
                </nav>
            </div>

            <div className={styles.rightSection}>
                <div className={styles.searchContainer}>
                    <input type="text" placeholder="Variable Search" className={styles.searchInput} />
                    <Search size={16} className={styles.searchIcon} />
                </div>
                <div
                    className={styles.profileContainer}
                    onMouseEnter={() => setShowDropdown(true)}
                    onMouseLeave={() => setShowDropdown(false)}
                >
                    <Link to="/settings" className={styles.profile}>
                        <img src={user?.avatar_url || defaultAvatar} alt="User Profile" className={styles.avatar} />
                    </Link>
                    {showDropdown && (
                        <div className={styles.dropdown}>
                            <button onClick={handleLogout} className={styles.dropdownItem}>
                                <LogOut size={16} />
                                <span>Sign Out</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};

export default Header;
