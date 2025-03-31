import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import React from 'react';
import GetDecks from './GetDecks';
import './App.css';

export const PageKawaii = () => {
  return (
    <div className="Kawaii">
      <GetDecks name="kawaii" />
    </div>
  );
};

export const PageKakkoii = () => {
  return (
    <div className="Kakkoii">
      <GetDecks name="kakkoii" />
    </div>
  );
};

export const PageTuyosou = () => {
  return (
    <div className="Tuyosou">
      <GetDecks name="tuyosou" />
    </div>
  );
};

export const PageYowasou = () => {
  return (
    <div className="Yowasou">
      <GetDecks name="yowasou" />
    </div>
  );
};

function App() {
  return (
      <BrowserRouter>
        <div className="App">
        <Routes>
          {/* exactをつけると完全一致になります。Homeはexactをつけてあげます */}
          <Route path="/kawaii" element={<PageKawaii />} />
          <Route path="/kakkoii" element={<PageKakkoii />} />
          <Route path="/tuyosou" element={<PageTuyosou />} />
          <Route path="/yowasou" element={<PageYowasou />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
export default App;