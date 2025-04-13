// frontend/src/components/ChatPanel.tsx
'use client'; // Add this directive for React hooks (useState, useEffect)

import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid'; // Import uuid to generate session IDs

// Define the structure for a message object
interface Message {
  role: 'user' | 'assistant' | 'system' | 'error'; // Added 'system' and 'error' roles
  content: string;
}

const ChatPanel: React.FC = () => {
  // State for the list of messages in the conversation
  const [messages, setMessages] = useState<Message[]>([
    // Initial welcome message
    { role: 'assistant', content: "Welcome! How can I help you plan your stay?" }
  ]);
  // State for the text currently typed in the input field
  const [inputValue, setInputValue] = useState<string>('');
  // State to track if waiting for a response from the backend
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // State to store the unique session ID for this chat instance
  const [sessionId, setSessionId] = useState<string>('');

  // Ref for the chat history div to enable auto-scrolling
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  // Generate a unique session ID when the component mounts
  useEffect(() => {
    setSessionId(uuidv4());
  }, []); // Empty dependency array ensures this runs only once on mount

  // Auto-scroll to the bottom of the chat history when messages change
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]); // Dependency array includes messages

  // Function to handle sending a message
  const handleSendMessage = async () => {
    // Trim whitespace and check if input is empty or loading
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading || !sessionId) {
      return; // Don't send empty messages or while loading or if no session ID
    }

    // Add user's message to the chat display immediately
    const userMessage: Message = { role: 'user', content: trimmedInput };
    setMessages(prevMessages => [...prevMessages, userMessage]);

    // Clear the input field
    setInputValue('');
    // Set loading state to true
    setIsLoading(true);

    try {
      // --- API Call to Backend ---
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chat`;

      const response = await fetch(apiUrl, { // Replace with env variable later
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: trimmedInput,
          session_id: sessionId,
        }),
      });

      setIsLoading(false); // Set loading to false after response or error

      if (!response.ok) {
        // Handle HTTP errors (e.g., 500 Internal Server Error)
        const errorData = await response.json().catch(() => ({ detail: 'Failed to parse error response.' }));
        console.error('API Error Response:', errorData);
        setMessages(prevMessages => [...prevMessages, { role: 'error', content: `Error: ${errorData.detail || response.statusText}` }]);
        return;
      }

      // Parse the JSON response from the backend
      const data = await response.json();

      // Add AI's response to the chat display
      if (data.reply) {
        const assistantMessage: Message = { role: 'assistant', content: data.reply };
        setMessages(prevMessages => [...prevMessages, assistantMessage]);
      } else {
         console.error('API response missing reply field:', data);
         setMessages(prevMessages => [...prevMessages, { role: 'error', content: 'Error: Received an invalid response from the server.' }]);
      }

    } catch (error) {
      setIsLoading(false); // Ensure loading is false on network error
      console.error('Failed to send message:', error);
      // Add an error message to the chat display
      setMessages(prevMessages => [...prevMessages, { role: 'error', content: 'Error: Could not connect to the backend service.' }]);
    }
  };

  // Handle Enter key press in the input field
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  // Function to render message bubbles based on role
  const renderMessage = (msg: Message, index: number) => {
    switch (msg.role) {
      case 'user':
        return (
            <div key={index} className="mb-4 text-right">
            <p className="bg-theme-highlight text-theme-primary p-3 rounded-lg border-2 border-theme-primary inline-block max-w-xs sm:max-w-md md:max-w-lg break-words">
              {msg.content}
            </p>
          </div>
        );
      case 'assistant':
        return (
            <div key={index} className="mb-4">
            <p className="bg-theme-background text-theme-primary p-3 rounded-lg border-2 border-theme-primary inline-block max-w-xs sm:max-w-md md:max-w-lg break-words">
              {msg.content}
            </p>
          </div>
        );
       case 'error':
        return (
            <div key={index} className="mb-4">
            <p className="bg-theme-accent text-theme-background p-3 rounded-lg border-2 border-theme-primary inline-block max-w-xs sm:max-w-md md:max-w-lg break-words">
              {msg.content}
            </p>
          </div>
        );
      default: // Handle system or other roles if needed, or ignore
        return null;
    }
  };


  return (
    // Main panel: Background, Primary border
    <main className="flex flex-col h-full bg-theme-background border-4 border-theme-primary m-4">
      {/* Conversation History Area */}
      <div ref={chatHistoryRef} className="flex-grow p-4 overflow-y-auto border-b-4 border-theme-primary">
        {messages.map(renderMessage)}
        {/* Loading indicator: Secondary background, Primary text */}
        {isLoading && (
           <div className="mb-4">
             <p className="bg-theme-secondary p-3 rounded-lg border-2 border-theme-primary inline-block animate-pulse text-theme-primary">
               AI is thinking...
             </p>
           </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t-theme-accent"> {/* Use theme color for border */}
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
             // Input: Background, Primary text/border
            className="flex-grow p-3 border-4 border-theme-secondary focus:outline-none text-theme-secondary bg-theme-background disabled:bg-gray-200 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading}
            // Button: Accent background, Primary text/border, Secondary hover
            className="bg-theme-accent p-3 border-4 border-theme-secondary font-bold text-theme-secondary hover:bg-theme-secondary disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? '...' : 'Send'}
          </button>
           {/* Add Voice Button later */}
        </div>
      </div>
    </main>
  );
};

export default ChatPanel;
