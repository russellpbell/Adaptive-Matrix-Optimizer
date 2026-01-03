import React, { useState, useEffect, useRef, useCallback } from 'react';

import styles from './AccountSettings.module.css';
import { uploadAvatar } from '../api';
import { useUser } from '../context/UserContext';
import Cropper from 'react-easy-crop';

const AccountSettings = () => {
    const { user, setUser, loading } = useUser();
    const [avatarUrl, setAvatarUrl] = useState('');
    const fileInputRef = useRef(null);

    // Crop state
    const [imageSrc, setImageSrc] = useState(null);
    const [crop, setCrop] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);
    const [isCropping, setIsCropping] = useState(false);

    useEffect(() => {
        if (user) {
            setAvatarUrl(user.avatar_url || "https://i.pravatar.cc/150?img=5");
        }
    }, [user]);

    const handleAvatarChange = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.addEventListener('load', () => {
                setImageSrc(reader.result);
                setIsCropping(true);
            });
            reader.readAsDataURL(file);
        }
        // Reset input
        event.target.value = null;
    };

    const onCropComplete = useCallback((croppedArea, croppedAreaPixels) => {
        setCroppedAreaPixels(croppedAreaPixels);
    }, []);

    const createImage = (url) =>
        new Promise((resolve, reject) => {
            const image = new Image();
            image.addEventListener('load', () => resolve(image));
            image.addEventListener('error', (error) => reject(error));
            image.setAttribute('crossOrigin', 'anonymous');
            image.src = url;
        });

    const getCroppedImg = async (imageSrc, pixelCrop) => {
        const image = await createImage(imageSrc);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = pixelCrop.width;
        canvas.height = pixelCrop.height;

        ctx.drawImage(
            image,
            pixelCrop.x,
            pixelCrop.y,
            pixelCrop.width,
            pixelCrop.height,
            0,
            0,
            pixelCrop.width,
            pixelCrop.height
        );

        return new Promise((resolve, reject) => {
            canvas.toBlob((blob) => {
                if (!blob) {
                    reject(new Error('Canvas is empty'));
                    return;
                }
                blob.name = 'cropped.jpeg';
                resolve(blob);
            }, 'image/jpeg');
        });
    };

    const handleCropSave = async () => {
        try {
            const croppedImageBlob = await getCroppedImg(imageSrc, croppedAreaPixels);
            const file = new File([croppedImageBlob], "avatar.jpg", { type: "image/jpeg" });

            const updatedUser = await uploadAvatar(file);
            setUser(updatedUser);
            setAvatarUrl(updatedUser.avatar_url);
            setIsCropping(false);
            setImageSrc(null);
        } catch (e) {
            console.error(e);
            alert("Failed to crop and upload image.");
        }
    };

    const handleCropCancel = () => {
        setIsCropping(false);
        setImageSrc(null);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className={styles.page}>

            <main className={styles.main}>
                <h1 className={styles.title}>Account Settings</h1>

                {isCropping && (
                    <div className={styles.cropModal}>
                        <div className={styles.cropContainer}>
                            <Cropper
                                image={imageSrc}
                                crop={crop}
                                zoom={zoom}
                                aspect={1}
                                onCropChange={setCrop}
                                onCropComplete={onCropComplete}
                                onZoomChange={setZoom}
                            />
                        </div>
                        <div className={styles.cropControls}>
                            <input
                                type="range"
                                value={zoom}
                                min={1}
                                max={3}
                                step={0.1}
                                aria-labelledby="Zoom"
                                onChange={(e) => setZoom(e.target.value)}
                                className={styles.zoomRange}
                            />
                            <div className={styles.cropButtons}>
                                <button className={styles.secondaryButton} onClick={handleCropCancel}>Cancel</button>
                                <button className={styles.primaryButton} onClick={handleCropSave}>Save Avatar</button>
                            </div>
                        </div>
                    </div>
                )}

                <div className={styles.grid}>
                    {/* Profile Section */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>Profile</h2>
                        <div className={styles.card}>
                            <div className={styles.profileHeader}>
                                <img src={avatarUrl} alt="Profile" className={styles.avatar} />
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    style={{ display: 'none' }}
                                    onChange={handleFileChange}
                                    accept="image/*"
                                />
                                <button className={styles.secondaryButton} onClick={handleAvatarChange}>Change Avatar</button>
                            </div>

                            <div className={styles.formGroup}>
                                <label>Full Name</label>
                                <input type="text" defaultValue={user?.full_name} className={styles.input} />
                            </div>

                            <div className={styles.formGroup}>
                                <label>Email Address</label>
                                <input type="email" defaultValue={user?.email} className={styles.input} />
                            </div>
                        </div>
                    </section>

                    {/* Organization Section */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>Organization</h2>
                        <div className={styles.card}>
                            <div className={styles.formGroup}>
                                <label>Organization Name</label>
                                <input type="text" defaultValue={user?.org_name} className={styles.input} />
                            </div>
                            <div className={styles.formGroup}>
                                <label>Role</label>
                                <input type="text" defaultValue="Senior Engineer" disabled className={`${styles.input} ${styles.disabled}`} />
                            </div>
                        </div>
                    </section>

                    {/* Security Section */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>Security</h2>
                        <div className={styles.card}>
                            <div className={styles.formGroup}>
                                <label>Current Password</label>
                                <input type="password" placeholder="••••••••" className={styles.input} />
                            </div>
                            <div className={styles.formGroup}>
                                <label>New Password</label>
                                <input type="password" placeholder="New password" className={styles.input} />
                            </div>
                            <button className={styles.primaryButton}>Update Password</button>
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
};

export default AccountSettings;
