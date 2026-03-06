// src/app/drive/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { driveService } from '../../services/driveService';

export default function DrivePage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const data = await driveService.listFiles();
        setFiles(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  if (loading) return <p style={{ padding: '20px' }}>Loading your Drive files...</p>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>My Google Drive Files</h1>
      {files.length > 0 ? (
        <ul>
          {files.map((file: any) => (
            <li key={file.id}>{file.name}</li>
          ))}
        </ul>
      ) : (
        <p>No files found or not authenticated.</p>
      )}
    </div>
  );
}