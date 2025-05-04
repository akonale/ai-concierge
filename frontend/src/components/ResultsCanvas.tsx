// frontend/src/components/ResultsCanvas.tsx
import React from 'react';

const PlaceholderCard: React.FC = () => {
  // Using Unsplash Source for a random yoga image
  const imageUrl = "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1999&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D";

  return (
    <div className="bg-white border-2 border-black p-4 mb-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
      {/* Actual Image */}
      <img
        src={imageUrl}
        alt="Yoga practice placeholder"
        className="w-full h-32 object-cover border-b-2 border-black mb-2" // Added object-cover
      />
      {/* Heading Placeholder */}
      <h3 className="text-lg font-bold text-black mb-1">Yoga Session</h3> {/* Updated heading */}
      {/* Text Placeholder */}
      <p className="text-sm text-black">
        Unwind with yoga session with our teacher
      </p>
    </div>
  );
};

const ResultsCanvas: React.FC = () => {
  return (
    // Canvas container: Light blue background, black left border, padding, scrollable
    <aside className="h-full bg-green-100 border-l-4 border-black p-4 overflow-y-auto">
      <h2 className="text-xl font-bold mb-4 text-black">Results</h2>
      {/* Placeholder Cards */}
      <PlaceholderCard />
      <PlaceholderCard />
      <PlaceholderCard />
    </aside>
  );
};

export default ResultsCanvas;
