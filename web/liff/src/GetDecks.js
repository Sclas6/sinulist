import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function GetDecks(type) {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get(`https://sclas.xyz/deck/${type.name}`)
      .then(response => {
        console.log(response.data.urls)
        setData(response.data.urls);
      })
      .catch(error => {
        console.error('There was an error!', error);
      });
  }, []);
  const cards = data.map((card, index) =>
    <img src={card} width="50%" height="50%"/>
  );

  return (
    <div>
      <Link to="/kawaii">可愛い女デッキ</Link><br></br>
      <Link to="/kakkoii">かっこいいデッキ</Link><br></br>
      <Link to="/tuyosou">つよそうデッキ</Link><br></br>
      <Link to="/yowasou">よわそうデッキ</Link>
      <br />
      {cards}
    </div>
  );
}

export default GetDecks;