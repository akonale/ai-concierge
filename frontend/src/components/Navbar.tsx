// frontend/src/components/Navbar.tsx
import React from 'react';

import { QuestionMarkCircleIcon, Cog6ToothIcon, Bars3Icon } from '@heroicons/react/24/outline'; // Example using Heroicons

// Define props to accept the toggle function from the parent component (page.tsx)
interface NavbarProps {
  onToggleSidebar: () => void; // Callback function to open/close the sidebar
}

const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  return (
    // Navbar container:
    // - Uses theme colors (bg-white, border-black) or fallbacks if not defined
    // - Flexbox for layout (justify-between, items-center)
    // - Responsive padding (p-2 on small screens, md:p-4 on medium+)
    // - Relative positioning and z-index to ensure it stays above potential overlays
    // - flex-shrink-0 prevents it from shrinking if container space is limited
    <nav className="bg-white border-b-4 border-black p-2 md:p-4 flex justify-between items-center relative z-20 flex-shrink-0">

      {/* Left Section: Hamburger Menu and Title */}
      <div className="flex items-center space-x-3 md:space-x-4">
        {/* Hamburger Button */}
        <button
          onClick={onToggleSidebar} // Call the function passed from the parent on click
          // Styling for the button: padding, text color, hover effect, focus outline
          className="p-1 md:p-2 text-black hover:bg-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-inset focus:ring-black"
          aria-label="Toggle sidebar" // Accessibility label
        >
          {/* Hamburger Icon SVG from Heroicons */}
          {/* Responsive icon size (h-6/w-6 on small, h-8/w-8 on medium+) */}
          <Bars3Icon className="h-6 w-6 md:h-8 md:w-8" />
        </button>

        {/* Title - Now aligned to the right of the hamburger */}
        {/* Text size adjusts responsively */}
        <h1 className="text-lg sm:text-xl md:text-2xl font-extrabold text-black whitespace-nowrap">
          AI Concierge
        </h1>
      </div>


      {/* Right Section: Icons */}
      <div className="flex items-center space-x-3 md:space-x-4">
         {/* Help Icon */}
         <button
            className="p-1 text-black hover:bg-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-inset focus:ring-black"
            aria-label="Help"
         >
            <QuestionMarkCircleIcon className="h-6 w-6 md:h-7 md:w-7" />
         </button>
         {/* Settings Icon */}
         <button
            className="p-1 text-black hover:bg-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-inset focus:ring-black"
            aria-label="Settings"
         >
            <Cog6ToothIcon className="h-6 w-6 md:h-7 md:w-7" />
         </button>
      </div>
    </nav>
  );
};


export default Navbar;
