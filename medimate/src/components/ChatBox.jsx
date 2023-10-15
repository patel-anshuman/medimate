import React, { useState, useEffect, useRef } from 'react';
// import axios from 'axios';
import './ChatBox.css';

import { Input } from "@chakra-ui/react";

function ChatBox({ conversation, setConversation, formatTime }) {
    const [question, setQuestion] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const conversationRef = useRef();
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    const [placeholders, setPlaceholders] = useState([
        "📅 Schedule an appointment",
        "📄 Upload prescription or ask for medication help",
        "🆘 Request emergency assistance",
        "💡 Get health tips and home remedies"
    ]);
    const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);

    useEffect(() => {
        if (conversationRef.current) {
            conversationRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [conversation]);

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

        const curr_ques = question;
        setConversation((prevConversation) => [
            ...prevConversation,
            { text: question, type: 'You', time: formatTime() },
        ]);
        setQuestion('');

        try {
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                body: JSON.stringify({ question: curr_ques }),
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();

            if (!response.ok) {
                console.error('Backend error:', data.error);

                setConversation([
                    ...conversation,
                    { text: '⚠️ Invalid response!!', type: 'Bot', time: formatTime() },
                ]);
            } else {
                const newMessage = {
                    text: data.message,
                    type: 'Bot',
                    time: formatTime(),
                };

                // Adding medicine recommendation if it exists in the response
                const recommendation = data.recommendation;
                if (recommendation) {
                    newMessage.recommendation = recommendation;
                }

                setConversation((prevConversation) => [...prevConversation, newMessage]);
            }
        } catch (error) {
            console.error('Error asking question:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = () => {
        const file = fileInputRef.current.files[0];
        if (file && file.type === 'application/pdf' && file.size <= 1024000) {
            const formData = new FormData();
            formData.append('pdfFile', file);

            fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log(data);
                    setConversation([
                        ...conversation,
                        { text: `Uploaded PDF: ${file.name}`, type: 'You', time: formatTime() }
                    ]);
                })
                .catch((error) => {
                    console.error('Error uploading PDF:', error);
                });
        } else {
            console.error('Invalid PDF file format or size exceeds 1MB');
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
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                    ref={fileInputRef}
                />
                <button
                    className="sc-btn"
                    onClick={() => fileInputRef.current.click()}
                >
                    📎
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
