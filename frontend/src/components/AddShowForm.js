// Add a show format code

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './styles.css';

const API_URL = 'http://localhost:8000';

const AddShowForm = () => {
  const [title, setTitle] = useState('');
  const [status, setStatus] = useState('Watching');
  const [currentEpisode, setCurrentEpisode] = useState(0);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/shows/`, {
        title,
        status,
        current_episode: currentEpisode,
      });
      navigate('/shows');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        alert(error.response.data.detail);
      } else {
        console.error('Failed to add show:', error);
      }
    }
  };

  return (
    <div>
      <h2>Add Show</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Status:</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            required
          >
            <option value="Watching">Watching</option>
            <option value="Completed">Completed</option>
            <option value="On Hold">On Hold</option>
            <option value="Dropped">Dropped</option>
          </select>
        </div>
        <div>
          <label>Episode:</label>
          <input
            type="number"
            value={currentEpisode}
            onChange={(e) => setCurrentEpisode(parseInt(e.target.value))}
            required
          />
        </div>
        <button className="button" type="submit">Add Show</button>
      </form>
    </div>
  );
};

export default AddShowForm;
