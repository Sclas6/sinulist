import React from 'react';
import { Link } from 'react-router-dom';

const Deck = () => {
  return (
    <div>
      <div>Home</div>
      <Link to='/about'>About</Link>
    </div>
  )
}

export default Deck;