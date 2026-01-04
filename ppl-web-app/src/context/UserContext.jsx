import React, { createContext, useState, useEffect, useContext } from 'react';
import { getCurrentUser } from '../api';

export const UserContext = createContext();

export const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                if (token === 'dummy_token_dev_mode') {
                    setUser({
                        id: 'dev_user',
                        email: 'dev@example.com',
                        is_active: true,
                        full_name: 'Developer'
                    });
                } else {
                    try {
                        const userData = await getCurrentUser();
                        setUser(userData);
                    } catch (error) {
                        console.error("Failed to fetch user", error);
                        localStorage.removeItem('token');
                    }
                }
            }
            setLoading(false);
        };

        fetchUser();
    }, []);

    const login = (token) => {
        localStorage.setItem('token', token);
        if (token === 'dummy_token_dev_mode') {
            setUser({
                id: 'dev_user',
                email: 'dev@example.com',
                is_active: true,
                full_name: 'Developer'
            });
        } else {
            // We'll refetch user data or set it directly if we had it
            // Ideally we fetch the user immediately after setting token
            getCurrentUser().then(setUser).catch(console.error);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <UserContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </UserContext.Provider>
    );
};
