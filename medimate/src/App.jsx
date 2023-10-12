import React, { useState, useEffect } from 'react';
import './App.css';
import logo from "./images/medimate.png"
import dot3 from "./images/3dot.png"
import save from "./images/save.png"
import clear from "./images/clear.png"

import ChatBox from './components/ChatBox';

import { IconButton } from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';


function App() {

  const [isBoxLoading, setIsBoxLoading] = useState(true);

  // useEffect(() => {
  //   const loadingTimeout = setTimeout(() => {
  //     setIsBoxLoading(false);
  //   }, 3000);

  //   return () => clearTimeout(loadingTimeout);
  // }, []);

  useEffect(() => {
    document.title = 'MediMate: Your personal health assist bot';
  }, []);

  return (
    <div className="App">
      <div>
        <header>
          <div>
            <div>
              <img src={logo} alt="logo" />
            </div>
            <div>
              <h1>MediMate</h1>
            </div>
          </div>
          <div>
            <button className='hd-btn'>
              <img src={clear} alt="clear" />
            </button>
            <button className='hd-btn'>
              <img src={save} alt="save" />
            </button>
            <button className='hd-btn'>
              <img src={dot3} alt="3 dot" />
            </button>
          </div>
        </header>
        {isBoxLoading ? (
          <div className="loading-visual">
            <div className="spinner"></div>
            <h3>Loading Chat...</h3>
          </div>
        ) : (
          <ChatBox />
        )}
      </div>
    </div>
  );
}

export default App;
