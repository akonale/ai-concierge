// frontend/src/app/page.tsx (Example using App Router)
'use client'; // Required for useState hook

import React, { useState, useEffect } from 'react'; // Import useState and useEffect
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import ChatPanel from '@/components/ChatPanel';
import ResultsCanvas from '@/components/ResultsCanvas'; // Import the new component
import { ExperienceCardData, DefaultExperiences } from '@/types'; // Import the type

export default function Home() {
  // State to hold the suggested experiences
  const [suggestions, setSuggestions] = useState<ExperienceCardData[] | null>(null);
  // State to track loading of default suggestions
  const [isLoadingDefaults, setIsLoadingDefaults] = useState<boolean>(true); // Start as true

  // Fetch default suggestions on component mount
  useEffect(() => {
    const fetchDefaultSuggestions = async () => {
      setIsLoadingDefaults(true); // Indicate loading start
      try {
        const apiUrl = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/experiences/default`;
        console.log("Fetching default suggestions from:", apiUrl);
        const response = await fetch(apiUrl);

        if (!response.ok) {
          console.error(`Error fetching default suggestions: ${response.status} ${response.statusText}`);
          // Optionally set suggestions to empty array or handle error state
          setSuggestions([]); // Set to empty array on error
          return; // Exit early
        }

        const defaultExp: DefaultExperiences = await response.json();
        const data: ExperienceCardData[] = defaultExp.default_experiences;
        console.log("Received default suggestions:", data);
        setSuggestions(data); // Update state with fetched data

      } catch (error) {
        console.error('Failed to fetch default suggestions:', error);
        // Optionally set suggestions to empty array or handle error state
        setSuggestions([]); // Set to empty array on fetch error
      } finally {
         setIsLoadingDefaults(false); // Indicate loading finished (success or error)
      }
    };

    fetchDefaultSuggestions();
  }, []); // Empty dependency array ensures this runs only once on mount

  return (
    <div className="flex flex-col h-screen bg-white"> {/* Changed background to white for consistency */}
      <Navbar />
      <div className="flex flex-grow overflow-hidden"> {/* Main layout container */}
        {/* Sidebar: Width is controlled internally by the component */}
        <Sidebar />
        {/* Chat Panel: Takes up the central flexible space */}
        <div className="flex-grow">
          {/* Pass the setter function to ChatPanel */}
          <ChatPanel onNewSuggestions={setSuggestions} />
        </div>
        {/* Results Canvas: Fixed width on the right */}
        <div className="w-1/4 flex-shrink-0"> {/* Adjust width as needed (e.g., w-96) */}
          {/* Pass the suggestions state and loading status to ResultsCanvas */}
          {/* Consider adding a loading indicator within ResultsCanvas based on isLoadingDefaults */}
          <ResultsCanvas suggestedExperiences={suggestions} isLoading={isLoadingDefaults} />
        </div>
      </div>
    </div>
  );
}

// Make sure your root layout (e.g., frontend/src/app/layout.tsx)
// allows the children to take full height, usually by setting h-screen on html and body.
// Example for frontend/src/app/layout.tsx:
// export default function RootLayout({ children }: { children: React.ReactNode }) {
//   return (
//     <html lang="en" className="h-full">
//       <body className="h-full">{children}</body>
//     </html>
//   );
// }
