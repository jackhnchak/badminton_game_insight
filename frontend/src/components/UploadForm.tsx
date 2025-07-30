import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UploadForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');
  const [taskId, setTaskId] = useState<string>('');
  const [downloadUrl, setDownloadUrl] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setStatus('Uploading...');
    const formData = new FormData();
    formData.append('video', file);

    try {
      const { data } = await axios.post('http://localhost:8000/api/upload', formData);
      setTaskId(data.task_id);
      setStatus('Processing...');
    } catch {
      setStatus('Upload failed');
    }
  };

  // Polling effect
  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(`http://localhost:8000/api/status/${taskId}`);
        if (data.state === 'SUCCESS') {
          // Build download URL
          setDownloadUrl(`http://localhost:8000/output/${data.result.split('/').pop()}`);
          setStatus('Done!');
          clearInterval(interval);
        } else if (data.state === 'FAILURE') {
          setStatus('Processing failed');
          clearInterval(interval);
        }
      } catch {
        setStatus('Error checking status');
        clearInterval(interval);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div className="bg-white p-6 rounded shadow">
      <h1 className="text-2xl mb-4">Upload Badminton Video</h1>
      <form onSubmit={handleSubmit} className="flex flex-col">
        <input type="file" accept="video/*" onChange={handleFileChange} required />
        <button type="submit" className="mt-4 bg-blue-500 text-white py-2 rounded">
          Process Video
        </button>
      </form>
      {status && <p className="mt-4">{status}</p>}
      {downloadUrl && (
        <p className="mt-2">
          <a href={downloadUrl} target="_blank" rel="noopener noreferrer">
            Download CSV
          </a>
        </p>
      )}
    </div>
  );
};

export default UploadForm;