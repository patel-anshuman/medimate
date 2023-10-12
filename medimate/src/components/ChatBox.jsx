import React, { useState, useEffect, useRef } from 'react';
// import axios from 'axios';
import './ChatBox.css';

import { Input } from "@chakra-ui/react";

function ChatBox({ conversation, setConversation, formatTime }) {
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const conversationRef = useRef(null);

    const handleQuestionChange = (e) => {
        setQuestion(e.target.value);
    };

    useEffect(() => {
        if (conversationRef.current) {
            const container = conversationRef.current;
            container.scrollTop = container.scrollHeight;
        }
    }, [conversation]);

    const handleSubmitQuestion = async () => {
        if (!question) return;

        setIsLoading(true);

        const curr_ques = question
        setConversation([...conversation,
        { text: question, type: 'You', time: formatTime() }
        ]);
        setQuestion('');

        try {
            const response = await fetch('http://127.0.0.1:5000/ask-question', {
                method: 'POST',
                body: JSON.stringify({ question: curr_ques }),
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            // console.log(response);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Backend error:', errorData.error);

                setConversation([
                    ...conversation,
                    { text: '⚠️ Invalid response!!', type: 'Bot', time: formatTime() }
                ]);

                return;
            }

            setConversation([
                ...conversation,
                { text: response.data[0].response, type: 'Bot', time: formatTime() }
            ]);

        } catch (error) {
            console.error('Error asking question:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-box">
            <div className="conversation" ref={conversationRef}>
                {conversation.map((message, index) => (
                    <div key={index} className={`message ${message.type}`}>
                        <p>
                            <b>{message.type}: </b>{message.text}
                        </p>
                        <span className="message-time">{message.time}</span>
                    </div>
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
                    placeholder="Ask MediMate about your health..."
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
