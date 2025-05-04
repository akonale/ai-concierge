// frontend/src/components/Sidebar.tsx
'use client'; // Required for useState

import React, { useState } from 'react';

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true); // State to control sidebar visibility

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    // Main container: Adjust width based on isOpen, add transition, set background to black
    <div className={`h-full bg-violet-500 border-r-4 border-black transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-16'}`}>
      {/* Toggle Button */}
      <div className="p-4 flex justify-end">
         {/* Keep button white for contrast */}
        <button
          onClick={toggleSidebar}
          className="p-2 border-2 border-black bg-white text-black hover:bg-gray-300 focus:outline-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
          aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
        >
          {/* Simple Hamburger/Close Icon SVG */}
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-6 h-6">
            {isOpen ? (
              // Close Icon (X)
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              // Hamburger Icon (3 lines)
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            )}
          </svg>
        </button>
      </div>

      {/* Sidebar Content (conditionally rendered or styled based on isOpen) */}
      <div className={`overflow-hidden transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
        {isOpen && ( // Render content only when open to avoid layout shifts or use visibility/opacity
          <div className="p-4">
            <h2 className="text-xl font-bold mb-4 text-white">Options</h2> {/* Changed text to white */}
            <ul className="space-y-2">
              {/* List items with neo-brutalistic style - Kept original styling */}
              <li className="border-2 bg-white border-black p-2 text-black hover:bg-yellow-300 cursor-pointer font-medium shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]">Experiences</li>
              <li className="border-2 bg-white border-black p-2 text-black hover:bg-yellow-300 cursor-pointer font-medium shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]">Activities</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
