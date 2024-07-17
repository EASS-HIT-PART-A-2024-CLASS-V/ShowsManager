// App frontend code

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import axios from 'axios';
import Home from './components/Home';
import ShowsList from './components/ShowsList';
import ImportShows from './components/ImportShows';
import AddShowForm from './components/AddShowForm';
import EditShowForm from './components/EditShowForm';

const API_URL = 'http://localhost:8000'; 

function App() {
  const createEmptyShowsList = async () => {
    try {
      const response = await axios.post(`${API_URL}/create-shows-list/`);
      if (response.status === 201) {
        console.log('Empty shows list created successfully!');
        window.location.href = '/shows';
      }
    } catch (error) {
      console.error('Failed to create shows list:', error);
    }
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home createEmptyShowsList={createEmptyShowsList} />} />
          <Route path="/shows" element={<ShowsList />} />
          <Route path="/import" element={<ImportShows />} />
          <Route path="/add-show" element={<AddShowForm />} />
          <Route path="/edit-show/:id" element={<EditShowForm />} /> {/* Add this route */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
