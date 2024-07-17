// Importing a show format code

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './styles.css';

const API_URL = 'http://localhost:8000';

const ImportShows = () => {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_URL}/import/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('Shows imported successfully!');
      navigate('/shows'); // Redirect to /shows after successful import
    } catch (error) {
      console.error('Failed to import shows:', error);
      alert('Failed to import shows. Please try again.');
    }
  };

  return (
    <div>
      <h2>Import Shows</h2>
      <input type="file" onChange={handleFileChange} />
      <button className="button" onClick={handleFileUpload}>Import</button>
    </div>
  );
};

export default ImportShows;
