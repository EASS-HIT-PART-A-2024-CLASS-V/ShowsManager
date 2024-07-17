// Loading show list format code

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate} from 'react-router-dom'; 
import './styles.css';

const API_URL = 'http://localhost:8000';

const ShowsList = () => {
    const [shows, setShows] = useState([]);
    const [filteredShows, setFilteredShows] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchShows();
    }, []);

    const fetchShows = async () => {
        try {
            const response = await axios.get(`${API_URL}/shows/`);
            setShows(response.data);
            setFilteredShows(response.data);
        } catch (error) {
            console.error('Failed to fetch shows:', error);
        }
    };

    const handleDelete = async (id) => {
        try {
            await axios.delete(`${API_URL}/shows/${id}`);
            fetchShows();
        } catch (error) {
            console.error('Failed to delete show:', error);
        }
    };

    const handleEdit = (id) => {
        navigate(`/edit-show/${id}`);
    };

    const handleSortByCategory = (category) => {
        if (category === 'All') {
            setFilteredShows(shows);
        } else {
            const filtered = shows.filter(show => show.status === category);
            setFilteredShows(filtered);
        }
    };

    const handleExport = async () => {
      try {
        const response = await axios.get('http://localhost:8000/export/', {
          responseType: 'blob',
        });
  
        const blob = new Blob([response.data], { type: 'application/json' });
  
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'shows.json';
        document.body.appendChild(a);
        a.click();
  
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
  
      } catch (error) {
        console.error('Failed to export shows:', error);
      }
    };

    return (
        <div>
            <h2>Shows List</h2>
            <div className="sort-buttons">
                <span>Sort:</span>
                <button className="button" onClick={() => handleSortByCategory('All')}>All</button>
                <button className="button" onClick={() => handleSortByCategory('Watching')}>Watching</button>
                <button className="button" onClick={() => handleSortByCategory('Completed')}>Completed</button>
                <button className="button" onClick={() => handleSortByCategory('On Hold')}>On Hold</button>
                <button className="button" onClick={() => handleSortByCategory('Dropped')}>Dropped</button>
            </div>
            <div className="container">
                <button className="button" onClick={() => navigate('/add-show')}>Add Show</button>
            </div>
            {filteredShows.length > 0 ? (
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Status</th>
                            <th>Episode</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredShows.map((show) => (
                            <tr key={show._id}>
                                <td>{show.title}</td>
                                <td>{show.status}</td>
                                <td>{show.current_episode}</td>
                                <td>
                                    <button className="button" onClick={() => handleEdit(show.id)}>Edit</button>
                                    <button className="button" onClick={() => handleDelete(show.id)}>Remove</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No shows available.</p>
            )}
            {filteredShows.length > 0 && (
                <div className="container">
                    <button className="button" onClick={handleExport}>Export Shows List</button>
                </div>
            )}
        </div>
    );
};

export default ShowsList;
