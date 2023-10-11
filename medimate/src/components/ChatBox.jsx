import React, { useState } from 'react';
import axios from 'axios';
import './ChatBox.css';

import { Input } from "@chakra-ui/react";

function ChatBox() {
    const [question, setQuestion] = useState('');
    const [conversation, setConversation] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleQuestionChange = (e) => {
        setQuestion(e.target.value);
    };

    const handleSubmitQuestion = async () => {
        if (!question) return;

        setIsLoading(true);

        try {
            const response = await axios.post('http://127.0.0.1:5000/ask-question', { question });
            // console.log(response);

            setConversation([
                ...conversation,
                { text: question, type: 'You' },
                { text: response.data[0].response, type: 'Bot' }, // Use response.data.response
            ]);

            setQuestion('');
        } catch (error) {
            console.error('Error asking question:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-box">
            <div className="conversation">
                {conversation.map((message, index) => (
                    <p key={index} className={`message ${message.type}`}>
                        <b>{message.type}: </b>{message.text}
                    </p>
                ))}
            </div>
            <div className="input-area">
                <button
                    className="sc-btn"
                // onClick={handleAttachFile}
                >📎
                </button>
                <Input
                    type="text"
                    placeholder="Ask a question..."
                    value={question}
                    onChange={handleQuestionChange}
                    onKeyDown={(e) => e.key === "Enter" && handleSubmitQuestion()}
                    _focus={{ outline: "none" }}
                />
                <button
                    className='sc-btn'
                // onClick={handleMicInput}
                >
                    🎙️
                </button>


                <button
                    onClick={handleSubmitQuestion}
                    disabled={isLoading}
                    size="sm"
                    className='pr-btn'
                >
                    {isLoading ? "Loading..." : "Send"}
                </button>
            </div>

        </div>
    );
}

export default ChatBox;
