// frontend/src/components/Sidebar.tsx
import React from 'react';

const Sidebar: React.FC = () => {
  return (
    <aside className="bg-white border-r-4 border-black p-4 shadow-[4px_0px_0px_0px_rgba(0,0,0,1)] h-full">
      <h2 className="text-xl font-bold mb-4">Options</h2>
      {/* Add sidebar content/links later */}
      <ul className="space-y-2">
        <li className="border-2 border-black p-2 hover:bg-yellow-300 cursor-pointer shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">Option 1</li>
        <li className="border-2 border-black p-2 hover:bg-yellow-300 cursor-pointer shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">Option 2</li>
      </ul>
    </aside>
  );
};

export default Sidebar;