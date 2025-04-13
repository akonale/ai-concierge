// frontend/src/components/Sidebar.tsx
import React from 'react';

const Sidebar: React.FC = () => {
return (
    // Use theme colors: background, primary border, primary text
    <aside className="bg-theme-background border-r-4 border-theme-primary p-4 text-theme-primary h-full">
    <h2 className="text-xl font-bold mb-4">Options</h2>
    {/* Add sidebar content/links later */}
    <ul className="space-y-2">
        {/* Example item using theme colors */}
        <li className="border-2 border-theme-primary p-2 hover:bg-theme-secondary hover:text-theme-primary cursor-pointer font-medium">Option 1</li>
        <li className="border-2 border-theme-primary p-2 hover:bg-theme-secondary hover:text-theme-primary cursor-pointer font-medium">Option 2</li>
    </ul>
    </aside>
);
};

export default Sidebar;