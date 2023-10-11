import React, { useState, useEffect } from 'react';
import './App.css';
import logo from "./images/medimate.png"
import dot3 from "./images/3dot.png"
import ChatBox from './components/ChatBox';

import { IconButton } from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';


function App() {

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
              <img src={dot3} alt="3 dot" />
            </button>
          </div>
        </header>
        <ChatBox />
      </div>
    </div>
  );
}

export default App;
