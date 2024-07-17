// Setting home page format code

import React from 'react';
import { Link } from 'react-router-dom';
import './styles.css';

const Home = ({ createEmptyShowsList }) => {
  return (
    <div>
      <h1>Welcome to the Shows Manager</h1>
      <button className="button" onClick={createEmptyShowsList}>Create a New List</button>
      <Link to="/import">
        <button className="button">Import Shows List</button>
      </Link>
    </div>
  );
};

export default Home;
