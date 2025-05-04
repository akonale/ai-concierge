// frontend/src/components/Navbar.tsx
import React from 'react';

import { QuestionMarkCircleIcon, Cog6ToothIcon } from '@heroicons/react/24/outline'; // Example using Heroicons

const Navbar: React.FC = () => {
  return (
    <nav className="bg-white border-b-4 border-theme-secondary p-4 text-theme-background flex justify-between items-center">
      <h1 className="text-2xl font-extrabold">AI Concierge</h1>
      <div className="flex items-center space-x-4">
        {/* Placeholder Icons - Replace with actual icons later */}
        <QuestionMarkCircleIcon className="h-6 w-6 text-theme-primary cursor-pointer hover:text-theme-accent" />
        <Cog6ToothIcon className="h-6 w-6 text-theme-primary cursor-pointer hover:text-theme-accent" />
      </div>
    </nav>
  );
};

export default Navbar;
