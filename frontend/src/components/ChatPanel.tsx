// frontend/src/components/ChatPanel.tsx
import React from 'react';

const ChatPanel: React.FC = () => {
  return (
    <main className="flex flex-col h-full bg-gray-100 border-4 border-black m-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
      {/* Conversation History Area */}
      <div className="flex-grow p-4 overflow-y-auto border-b-4 border-black">
        {/* Placeholder for messages */}
        <div className="mb-4">
          <p className="bg-white p-3 rounded-lg border-2 border-black inline-block shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            AI: Welcome! How can I help you plan your stay?
          </p>
        </div>
        <div className="mb-4 text-right">
          <p className="bg-yellow-300 p-3 rounded-lg border-2 border-black inline-block shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            User: I want relaxing activities.
          </p>
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t-black"> {/* Removed redundant border class */}
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Type your message..."
            className="flex-grow p-3 border-4 border-black focus:outline-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
          />
          <button className="bg-yellow-300 p-3 border-4 border-black font-bold hover:bg-yellow-400 active:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] active:translate-x-[2px] active:translate-y-[2px] shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            Send
          </button>
           {/* Add Voice Button later */}
        </div>
      </div>
    </main>
  );
};

export default ChatPanel;