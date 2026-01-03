import React, { useState, useRef, useEffect } from 'react';
import styles from './TagSelector.module.css';

const MOCK_TAGS = [
    "TI-101", "FIC-204", "PI-12345", "TI-23456", "PI-34567",
    "T-1001 RR", "Ethylene Product", "Benzene Product", "C-1001",
    "P-1002", "P-2001", "C-1002", "LI-505", "FI-602",
    "TI-701", "PI-808", "AI-909", "XV-111", "ZS-222", "HS-333"
];

const TagSelector = ({ value, onChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const containerRef = useRef(null);

    const filteredTags = MOCK_TAGS.filter(tag =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
    );

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleSelect = (tag) => {
        onChange(tag);
        setSearchTerm(tag);
        setIsOpen(false);
    };

    return (
        <div className={styles.container} ref={containerRef}>
            <label className={styles.label}>Tag ID / Calculation <span className={styles.italic}>(if applicable)</span></label>
            <div className={styles.inputWrapper}>
                <input
                    type="text"
                    className={styles.input}
                    value={searchTerm || value}
                    onChange={(e) => {
                        setSearchTerm(e.target.value);
                        setIsOpen(true);
                        onChange(e.target.value); // Allow free text or filter
                    }}
                    onFocus={() => setIsOpen(true)}
                    placeholder="Select or type tag..."
                />
                <span className={styles.arrow}>▼</span>

                {isOpen && filteredTags.length > 0 && (
                    <ul className={styles.dropdown}>
                        {filteredTags.map(tag => (
                            <li
                                key={tag}
                                className={styles.option}
                                onClick={() => handleSelect(tag)}
                            >
                                {tag}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default TagSelector;
