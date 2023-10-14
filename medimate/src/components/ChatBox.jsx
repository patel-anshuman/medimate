import React, { useState, useEffect, useRef } from 'react';
// import axios from 'axios';
import './ChatBox.css';

import { Input } from "@chakra-ui/react";

function ChatBox({ conversation, setConversation, formatTime }) {
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const [placeholders, setPlaceholders] = useState([
        "📅 Schedule an appointment",
        "📄 Upload prescription or ask for medication help",
        "🆘 Request emergency assistance",
        "💡 Get health tips and home remedies"
    ]);
    const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentPlaceholderIndex((prevIndex) => (prevIndex + 1) % placeholders.length);
        }, 5000); // Change placeholder every 5 seconds

        return () => {
            clearInterval(interval);
        };
    }, [currentPlaceholderIndex, placeholders]);

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

            const newMessage = {
                text: response.data[0].response,
                type: 'Bot',
                time: formatTime(),
            };

            // Adding medicine reccomendation if it exists in response
            const recommendation = response.data[0].recommendation;
            if (recommendation) {
                newMessage.recommendation = recommendation;
            }

            setConversation([...conversation, newMessage]);

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
                        {message.recommendation && message.recommendation.length > 0 && (
                            <div>
                                {message.recommendation.map((med, medIndex) => (
                                    <div key={medIndex}>
                                        <img src={med.img} alt={med.name[0]} />
                                        <p>{med.name}</p>
                                        <p>MRP: ₹{med.price}</p>
                                        <a href="#">Buy</a>
                                    </div>
                                ))}
                            </div>
                        )}
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
                    placeholder={`Ask to ${placeholders[currentPlaceholderIndex]}...`}
                    value={question}
                    onChange={handleQuestionChange}
                    onKeyDown={(e) => e.key === "Enter" && handleSubmitQuestion()}
                    className="smooth-transition"
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
