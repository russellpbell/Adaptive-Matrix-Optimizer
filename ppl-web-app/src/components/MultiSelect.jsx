import React, { useState, useRef, useEffect } from 'react';
import { X } from 'lucide-react';
import styles from './MultiSelect.module.css';

const MultiSelect = ({
    value = [],
    onChange,
    placeholder = "Type and press Enter...",
    options = [],
    restrictToOptions = false
}) => {
    const [inputValue, setInputValue] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef(null);

    // Filter options based on input
    const filteredOptions = options.filter(opt =>
        opt.toLowerCase().includes(inputValue.toLowerCase()) && !value.includes(opt)
    );

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (containerRef.current && !containerRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addTag(inputValue);
        }
    };

    const addTag = (tag) => {
        const trimmedTag = tag.trim();
        if (!trimmedTag) return;

        // If restricted, check if it exists in options
        if (restrictToOptions) {
            const match = options.find(opt => opt.toLowerCase() === trimmedTag.toLowerCase());
            if (match) {
                onChange([...value, match]);
                setInputValue('');
                setIsOpen(false);
            }
        } else {
            // Free text allowed
            if (!value.includes(trimmedTag)) {
                onChange([...value, trimmedTag]);
                setInputValue('');
                setIsOpen(false);
            }
        }
    };

    const removeTag = (tagToRemove) => {
        onChange(value.filter(tag => tag !== tagToRemove));
    };

    return (
        <div className={styles.container} ref={containerRef}>
            <div className={styles.tagsWrapper} onClick={() => setIsOpen(true)}>
                {value.map((tag, index) => (
                    <span key={index} className={styles.tag}>
                        {tag}
                        <button
                            className={styles.removeButton}
                            onClick={(e) => { e.stopPropagation(); removeTag(tag); }}
                        >
                            <X size={12} />
                        </button>
                    </span>
                ))}
                <input
                    type="text"
                    className={styles.input}
                    value={inputValue}
                    onChange={(e) => {
                        setInputValue(e.target.value);
                        setIsOpen(true);
                    }}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setIsOpen(true)}
                    placeholder={value.length === 0 ? placeholder : ""}
                />
            </div>

            {/* Dropdown for options */}
            {isOpen && options.length > 0 && filteredOptions.length > 0 && (
                <ul className={styles.dropdown}>
                    {filteredOptions.map(opt => (
                        <li
                            key={opt}
                            className={styles.option}
                            onClick={() => addTag(opt)}
                        >
                            {opt}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default MultiSelect;
