// frontend/src/components/Sidebar.tsx
'use client';

import React from 'react';
// Import Heroicons for the close button
import { XMarkIcon } from '@heroicons/react/24/outline';

// Define props passed from the parent component (page.tsx)
interface SidebarProps {
  isOpen: boolean; // Controls visibility and state
  onClose: () => void; // Function to signal closing the sidebar
}

// Helper function to check if the screen size is desktop (md breakpoint or larger)
// Can be moved to a utils file
const isDesktop = () => typeof window !== 'undefined' && window.innerWidth >= 768;

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {

  // Base classes applied regardless of screen size or state
  const panelBaseClasses = "h-full bg-violet-200 border-r-4 border-black transition-all duration-300 ease-in-out flex flex-col";

  // Classes defining mobile-specific overlay behavior (applied below md breakpoint)
  // Uses fixed positioning, z-index, and transform for sliding effect
  const mobileClasses = `fixed top-0 left-0 z-40 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'}`;

  // Classes defining desktop-specific static/push behavior (applied md breakpoint and up)
  // Uses relative positioning (default), removes transform, sets specific widths based on isOpen
  const desktopClasses = `md:relative md:transform-none md:z-auto ${isOpen ? 'md:w-64' : 'md:w-16'}`; // Control width on desktop

  // Classes for the overlay background (dimming effect)
  // Applied only when sidebar is open AND screen is mobile (hidden on md+)
  const overlayClasses = `fixed inset-0 z-30 bg-black bg-opacity-60 transition-opacity duration-300 ease-in-out md:hidden ${ // Hide overlay on desktop
    isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
  }`;

  return (
    <> {/* Fragment to return multiple elements */}

      {/* Overlay Background (Mobile Only) */}
      {/* Clicking this closes the sidebar on mobile */}
      <div
        className={overlayClasses}
        onClick={onClose}
        aria-hidden="true"
      ></div>

      {/* Sidebar Panel */}
      {/* Combines base, mobile, and desktop classes for responsive behavior */}
      <div
        className={`${panelBaseClasses} ${mobileClasses} ${desktopClasses}`}
        // Explicit width for mobile when open (Tailwind classes handle desktop width)
        style={ !isDesktop() && isOpen ? { width: '16rem' } : {} } // w-64 equivalent
        role="dialog"
        aria-modal={!isDesktop()} // Only acts as a modal overlay on mobile
        aria-labelledby="sidebar-title"
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-black flex-shrink-0">
          {/* Title - Hidden via class when collapsed on desktop */}
          <h2 id="sidebar-title" className={`text-xl font-bold text-white ${!isOpen && 'md:hidden'}`}>Options</h2>
          {/* Close Button - Hidden via class when collapsed on desktop */}
          {/* On mobile, this button is inside the sliding panel */}
          <button
            onClick={onClose}
            className={`p-1 text-white hover:bg-violet-700 rounded focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white ${
                !isOpen && 'md:hidden' // Hide close button when collapsed on desktop
            }`}
            aria-label="Close sidebar"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Sidebar Content Area */}
        {/* Content fades/hides when collapsed on desktop for a cleaner look */}
        {/* overflow-y-auto handles scrolling */}
        <div className={`p-4 overflow-y-auto flex-grow transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 md:opacity-100'}`}>
           {/* Conditionally render full list items or icons */}
           {isOpen ? (
             // Render full list when sidebar is open
             <ul className="space-y-2">
               <li className="border-2 bg-white border-black p-2 text-black hover:bg-yellow-300 cursor-pointer font-medium shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]">Experiences</li>
               <li className="border-2 bg-white border-black p-2 text-black hover:bg-yellow-300 cursor-pointer font-medium shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]">Activities</li>
             </ul>
           ) : (
             // Render icons only when collapsed on desktop (hidden on mobile when collapsed)
             <div className="hidden md:block mt-4 space-y-4">
                {/* Example Icon Placeholders - Replace with actual icons */}
                <div className="h-8 w-8 mx-auto bg-white border-2 border-black flex items-center justify-center text-black" title="Experiences">E</div>
                <div className="h-8 w-8 mx-auto bg-white border-2 border-black flex items-center justify-center text-black" title="Activities">A</div>
             </div>
           )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
