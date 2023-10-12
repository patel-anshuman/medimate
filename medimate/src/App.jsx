import React, { useState, useEffect } from 'react';
import './App.css';
import logo from "./images/medimate.png"
import dot3 from "./images/3dot.png"
import save from "./images/save.png"
import clear from "./images/clear.png"

import ChatBox from './components/ChatBox';


function App() {

  const [isBoxLoading, setIsBoxLoading] = useState(false); // initially true
  const [conversation, setConversation] = useState([{
    type: 'Bot',
    text: 'Welcome to MediMate! How can I assist you with your health today?',
    time: formatTime(new Date())
  }]);

  // useEffect(() => {
  //   const loadingTimeout = setTimeout(() => {
  //     setIsBoxLoading(false);
  //   }, 3000);

  //   return () => clearTimeout(loadingTimeout);
  // }, []);

  useEffect(() => {
    document.title = 'MediMate: Your personal health assist bot';
  }, []);

  function formatTime(date) {
    const options = { hour: 'numeric', minute: 'numeric', hour12: true };
    return new Intl.DateTimeFormat('en-US', options).format(date);
  }

  const clearConversation = () => {
    setConversation([{
      type: 'Bot',
      text: 'Welcome to MediMate! How can I assist you with your health today?',
      time: formatTime(new Date())
    }]);
  };

  const saveConversation = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/save-convo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Set the content type to JSON
        },
        body: JSON.stringify({ conversation }), // Convert the data to JSON string
      });

      if (response.ok) {
        const responseData = await response.json();
        // Handle the response data if needed
        console.log('Conversation saved to backend:', responseData);
      } else {
        throw new Error('Failed to save conversation');
      }
    } catch (error) {
      // Handle any errors that occur during the POST request
      console.error('Error saving conversation:', error);
    }
  };

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
            <button className='hd-btn' onClick={clearConversation}>
              <img src={clear} alt="clear" />
            </button>
            <button className='hd-btn' onClick={saveConversation}>
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
          <ChatBox conversation={conversation} setConversation={setConversation} formatTime={formatTime}/>
        )}
      </div>
    </div>
  );
}

export default App;
