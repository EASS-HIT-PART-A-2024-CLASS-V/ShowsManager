// Edit a show format code

  import React, { useState, useEffect } from 'react';
  import axios from 'axios';
  import { useParams, useNavigate } from 'react-router-dom';
  import './styles.css';

  const API_URL = 'http://localhost:8000';

  const EditShowForm = () => {
    const { id } = useParams();
    const [title, setTitle] = useState('');
    const [status, setStatus] = useState('Watching');
    const [currentEpisode, setCurrentEpisode] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
      const fetchShow = async () => {
        try {
          if (!id) return;

          const response = await axios.get(`${API_URL}/shows/${id}`);
          const { title, status, current_episode } = response.data;
          setTitle(title);
          setStatus(status);
          setCurrentEpisode(current_episode);
        } catch (error) {
          console.error('Failed to fetch show:', error);
        }
      };

      fetchShow();
    }, [id]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        if (!id) {
          console.error('Show ID is undefined');
          return; // Prevents submitting with undefined id
        }
        
        await axios.put(`${API_URL}/shows/${id}`, {
          title,
          status,
          current_episode: currentEpisode,
        });
        navigate('/shows');
      } catch (error) {
        console.error('Failed to update show:', error);
      }
    };

    return (
      <div>
        <h2>Edit Show</h2>
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
          <button className="button" type="submit">Update Show</button>
        </form>
      </div>
    );
  };

  export default EditShowForm;