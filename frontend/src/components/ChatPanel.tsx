// frontend/src/components/ChatPanel.tsx
'use client'; // Add this directive for React hooks (useState, useEffect)

import React, { useState, useEffect, useRef, useCallback } from 'react'; // Added useCallback
import { v4 as uuidv4 } from 'uuid'; // Import uuid to generate session IDs

// Define the structure for a message object
interface Message {
  id: string; // Unique ID for each message
  role: 'user' | 'assistant' | 'system' | 'error'; // Added 'system' and 'error' roles
  content: string;
}

const ChatPanel: React.FC = () => {
  // State for the list of messages in the conversation
  const [messages, setMessages] = useState<Message[]>([
    // Initial welcome message
    { id: uuidv4(), role: 'assistant', content: "Welcome! How can I help you plan your stay?" }
  ]);
  // State for the text currently typed in the input field
  const [inputValue, setInputValue] = useState<string>('');
  // State to track if waiting for a response from the backend
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // State to store the unique session ID for this chat instance
  const [sessionId, setSessionId] = useState<string>('');
  // State for recording status
  const [isRecording, setIsRecording] = useState<boolean>(false);

  // Ref for the chat history div to enable auto-scrolling
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  // Refs for MediaRecorder and audio chunks to avoid re-renders
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

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


  // Function to send recorded audio to the backend
  const sendAudioToBackend = useCallback(async (audioBlob: Blob) => {
    if (!sessionId) {
      console.error("Session ID is missing, cannot send audio.");
      setMessages(prev => [...prev, { id: uuidv4(), role: 'error', content: 'Error: Session ID missing.' }]);
      return;
    }
    if (audioBlob.size === 0) {
        console.error("Audio blob is empty, not sending.");
        // Optionally inform the user
        // setMessages(prev => [...prev, { role: 'system', content: 'Recording was empty.' }]);
        return;
    }

    console.log("Sending audio blob:", audioBlob);
    setIsLoading(true); // Indicate loading state

    const formData = new FormData();
    // Whisper needs a filename to help determine the format.
    // Browsers often record in webm or ogg with opus codec. '.webm' is a safe bet.
    formData.append('audio_file', audioBlob, 'recording.webm');
    formData.append('session_id', sessionId);

    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/audio`;
      console.log("API Base URL (Audio):", process.env.NEXT_PUBLIC_API_BASE_URL); // Added log
      console.log("Constructed API URL (Audio):", apiUrl); // Added log
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData, // Send FormData directly, fetch handles headers
      });

      setIsLoading(false); // Reset loading state

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to parse error response.' }));
        console.error('API Error Response (Audio):', errorData);
        setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: `Audio Error: ${errorData.detail || response.statusText}` }]);
        return;
      }

      const data = await response.json();
      // Log the entire received data object immediately after parsing JSON
      console.log("Received data from /api/v1/audio:", JSON.stringify(data, null, 2));
      const newMessages: Message[] = [];

      // Add transcribed user message if it exists as a non-empty string
      if (typeof data.transcribed_text === 'string' && data.transcribed_text.length > 0) {
        // Log specifically when deciding to display the message
        console.log("Displaying transcribed text:", data.transcribed_text);
        const userMessage: Message = { id: uuidv4(), role: 'user', content: data.transcribed_text };
        newMessages.push(userMessage);
      } else if (typeof data.transcribed_text === 'string' && data.transcribed_text.length === 0) {
         // Log that transcription resulted in an empty string (e.g., silence recorded or transcription failed)
         console.log('Received empty transcription text from backend.');
      } else {
         // Log if the field is missing or not a string (shouldn't happen with current backend model)
         console.warn('API response issue: transcribed_text field missing or not a string:', data);
      }

      // Add AI's response if available
      if (data.reply) {
        const assistantMessage: Message = { id: uuidv4(), role: 'assistant', content: data.reply };
        newMessages.push(assistantMessage);
      } else {
        console.error('API response missing reply field (Audio):', data);
        // Add error only if reply is missing, transcription might be optional
        setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: 'Error: Received an invalid response from the server (missing reply).' }]);
      }

      // Add the new messages (transcription + reply) to the state
      if (newMessages.length > 0) {
        setMessages(prevMessages => [...prevMessages, ...newMessages]);
      }

    } catch (error) {
      setIsLoading(false);
      console.error('Failed to send audio message:', error);
      setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: 'Error: Could not connect to the backend service for audio.' }]);
    }
  }, [sessionId]); // Dependency: sessionId


  // Function to handle microphone button clicks (start/stop recording)
  const handleMicClick = useCallback(async () => {
    if (isRecording) {
      // --- Stop Recording ---
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop(); // Triggers 'onstop' event
        // State update (isRecording=false) happens in onstop handler
         console.log("Stopping recording...");
      }
    } else {
      // --- Start Recording ---
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error("getUserMedia not supported on your browser!");
        setMessages(prev => [...prev, { id: uuidv4(), role: 'error', content: 'Error: Audio recording is not supported on your browser.' }]);
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = []; // Clear previous chunks

        // Event handler when data becomes available
        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
             console.log("Audio chunk received, size:", event.data.size);
          }
        };

        // Event handler when recording stops
        mediaRecorderRef.current.onstop = () => {
          console.log("Recording stopped, processing audio chunks...");
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' }); // Specify MIME type
          sendAudioToBackend(audioBlob); // Send the complete audio
          audioChunksRef.current = []; // Clear chunks after processing
          // Stop tracks to release microphone resource
          stream.getTracks().forEach(track => track.stop());
          setIsRecording(false); // Update state after stopping
           console.log("Microphone released.");
        };

        // Start recording
        mediaRecorderRef.current.start();
        setIsRecording(true); // Update state
        console.log("Recording started...");

      } catch (err) {
        console.error("Error accessing microphone:", err);
        let errorMessage = 'Error: Could not access microphone.';
        if (err instanceof Error) {
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMessage = 'Error: Microphone permission denied. Please allow access in your browser settings.';
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                  errorMessage = 'Error: No microphone found. Please ensure one is connected and enabled.';
             }
         }
        setMessages(prev => [...prev, { id: uuidv4(), role: 'error', content: errorMessage }]);
      }
    }
  }, [isRecording, sendAudioToBackend]); // Dependencies: isRecording state and the sendAudio function


  // Function to handle sending a message
  const handleSendMessage = async () => {
    // Trim whitespace and check if input is empty or loading
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading || !sessionId) {
      return; // Don't send empty messages or while loading or if no session ID
    }

    // Add user's message to the chat display immediately
    const userMessage: Message = { id: uuidv4(), role: 'user', content: trimmedInput };
    setMessages(prevMessages => [...prevMessages, userMessage]);

    // Clear the input field
    setInputValue('');
    // Set loading state to true
    setIsLoading(true);

    try {
      // --- API Call to Backend ---
      const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chat`;
      console.log("API Base URL (Chat):", process.env.NEXT_PUBLIC_API_BASE_URL); // Added log
      console.log("Constructed API URL (Chat):", apiUrl); // Added log
      
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
        setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: `Error: ${errorData.detail || response.statusText}` }]);
        return;
      }

      // Parse the JSON response from the backend
      const data = await response.json();

      // Add AI's response to the chat display
      if (data.reply) {
        const assistantMessage: Message = { id: uuidv4(), role: 'assistant', content: data.reply };
        setMessages(prevMessages => [...prevMessages, assistantMessage]);
      } else {
         console.error('API response missing reply field:', data);
         setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: 'Error: Received an invalid response from the server.' }]);
      }

    } catch (error) {
      setIsLoading(false); // Ensure loading is false on network error
      console.error('Failed to send message:', error);
      // Add an error message to the chat display
      setMessages(prevMessages => [...prevMessages, { id: uuidv4(), role: 'error', content: 'Error: Could not connect to the backend service.' }]);
    }
  };

  // Handle Enter key press in the input field
  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  // Function to render message bubbles based on role
  const renderMessage = (msg: Message) => { // Removed index parameter
    switch (msg.role) {
      case 'user':
        return (
            <div key={msg.id} className="mb-4 flex justify-end"> {/* Use msg.id as key, ensure right alignment */}
            <p className="bg-yellow-300 text-black p-3 rounded-none border-2 border-black inline-block max-w-xs sm:max-w-md md:max-w-lg break-words shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"> {/* Neo-brutalist shadow */}
              {msg.content}
            </p>
          </div>
        );
      case 'assistant':
        return (
            <div key={msg.id} className="mb-4 flex justify-start"> {/* Use msg.id as key, ensure left alignment */}
            <p className="bg-white text-black p-3 rounded-none border-2 border-black inline-block max-w-xs sm:max-w-md md:max-w-lg break-words shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"> {/* Neo-brutalist shadow */}
              {msg.content}
            </p>
          </div>
        );
       case 'error':
        return (
            <div key={msg.id} className="mb-4 flex justify-start"> {/* Use msg.id as key, ensure left alignment */}
            <p className="bg-red-500 text-white p-3 rounded-none border-2 border-black inline-block max-w-xs sm:max-w-md md:max-w-lg break-words shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"> {/* Neo-brutalist shadow */}
              {msg.content}
            </p>
          </div>
        );
      default: // Handle system or other roles if needed, or ignore
        return null;
    }
  };


  return (
    // Main panel: White background, Black border
    <main className="flex flex-col h-full bg-white border-4 border-black m-4">
      {/* Conversation History Area */}
      <div ref={chatHistoryRef} className="flex-grow p-4 overflow-y-auto border-b-4 border-black">
        {messages.map(renderMessage)}
        {/* Loading indicator: White background, Black border/text */}
        {isLoading && (
           <div className="mb-4 flex justify-start">
             <p className="bg-white text-black p-3 rounded-none border-2 border-black inline-block animate-pulse">
               AI is thinking...
             </p>
           </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t-4 border-black"> {/* Black border */}
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading || isRecording} // Disable input while loading or recording
             // Input: White background, Black text/border, no rounded corners
            className="flex-grow p-3 border-4 border-black rounded-none focus:outline-none text-black bg-white disabled:bg-gray-200 disabled:cursor-not-allowed"
          />
          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={isLoading || isRecording || !inputValue.trim()} // Disable send when loading, recording, or input is empty
            // Button: Black background, White text, Black border, Gray hover, no rounded corners
            className="bg-black p-3 border-4 border-black rounded-none font-bold text-white hover:bg-gray-800 disabled:bg-gray-400 disabled:text-gray-700 disabled:border-gray-500 disabled:cursor-not-allowed"
          >
            {isLoading && !isRecording ? '...' : 'Send'} {/* Show loading only if not recording */}
          </button>
          {/* Microphone Button */}
          <button
            onClick={handleMicClick}
            disabled={isLoading} // Disable mic only when actively sending/processing (text or audio)
            title={isRecording ? "Stop Recording" : "Start Recording"}
            // Button: Black background/border, White text, Gray hover, Red background when recording
            className={`p-3 border-4 border-black rounded-none font-bold text-white hover:bg-gray-800 disabled:bg-gray-400 disabled:text-gray-700 disabled:border-gray-500 disabled:cursor-not-allowed ${
              isRecording ? 'bg-red-600 hover:bg-red-700' : 'bg-black' // Red background when recording
            }`}
          >
            {/* Simple SVG Mic Icon - Ensure stroke is white for visibility on dark backgrounds */}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
};

export default ChatPanel;
