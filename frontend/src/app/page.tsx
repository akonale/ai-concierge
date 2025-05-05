// frontend/src/app/page.tsx (Example using App Router)
'use client'; // Required for useState hook

import React, { useState, useEffect } from 'react';
// Assuming components are in @/components and types in @/types
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import ChatPanel from '@/components/ChatPanel';
import ResultsCanvas from '@/components/ResultsCanvas'; // Import the new component
import { ExperienceCardData, DefaultExperiences } from '@/types'; // Import the type

// Helper function to check screen size (consider moving to utils)
const isDesktop = () => typeof window !== 'undefined' && window.innerWidth >= 768; // 768px is Tailwind's 'md' breakpoint

export default function Home() {
    // State to hold the suggested experiences
  const [suggestions, setSuggestions] = useState<ExperienceCardData[] | null>(null);
  // State to track loading of default suggestions
  const [isLoadingDefaults, setIsLoadingDefaults] = useState<boolean>(true); // Start as true

  // // State for the results data passed between ChatPanel and ResultsCanvas
  // const [resultsState, setResultsState] = useState<ExperienceCardData[] | null>(null);
  // // State for loading indicators (e.g., when fetching default experiences)
  // const [isInitialLoading, setIsInitialLoading] = useState<boolean>(false); // Set true if fetching defaults
  // State for controlling the overlay sidebar visibility, managed here
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false); // Default closed

    // --- Handle Resize ---
  // Adjust sidebar state if window is resized across the breakpoint
  useEffect(() => {
    const handleResize = () => {
      // Only automatically open/close on resize if it crosses the md threshold
      // You might want more nuanced logic depending on user interaction preference
      if (isDesktop()) {
        // If resizing to desktop, ensure it's open (or restore previous desktop state)
        // setIsSidebarOpen(true); // Simplest: always open on resize to desktop
      } else {
        // If resizing to mobile, ensure it's closed
        setIsSidebarOpen(false);
      }
    };

    // Set initial state correctly after hydration on client
    setIsSidebarOpen(isDesktop());

    window.addEventListener('resize', handleResize);
    // Cleanup listener on component unmount
    return () => window.removeEventListener('resize', handleResize);
  }, []); // Empty array ensures this runs only on mount and unmount


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

      // Callback function passed to Navbar and Sidebar to toggle visibility
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    // Main container: Full screen height, flex column layout, overflow hidden prevents scrolling the whole page
    <div className="flex flex-col h-screen bg-theme-background overflow-hidden"> {/* Use theme background if defined */}

      {/* Navbar Component: Receives the toggle function */}
      <Navbar onToggleSidebar={toggleSidebar} />

            {/* Main Content Area */}
      <div className="flex flex-grow overflow-hidden">
      {/* Sidebar Component: Rendered conditionally based on state */}
      {/* It uses fixed positioning and handles its own overlay */}
      <Sidebar isOpen={isSidebarOpen} onClose={toggleSidebar} />

      {/* Main Content Area Container */}
      {/* Uses Flexbox. Stacks vertically by default (mobile). Becomes a row on medium screens+ */}
      {/* flex-grow allows this area to take remaining vertical space. overflow-hidden prevents internal content from spilling out */}
      {/* Content Wrapper */}
        {/* This div wraps the Chat + Results columns */}
        {/* On desktop (md+), its left margin changes based on sidebar state */}
        {/* Added transition for smooth resizing */}
        <div className={`flex flex-col md:flex-row flex-grow overflow-hidden transition-all duration-300 ease-in-out`}>

        {/* Primary Content Column (Chat + Mobile Results) */}
        {/* Takes full width on mobile, specific width on desktop. */}
        {/* flex-col ensures ChatPanel and ResultsCanvas stack vertically within this column */}
        {/* overflow-hidden prevents content spill */}
        <div className="flex flex-col flex-grow w-full md:w-3/5 lg:w-2/3 overflow-hidden">

          {/* Chat Panel Container */}
          {/* flex-grow allows it to take most vertical space in this column */}
          {/* h-0 and min-h-0 are important flexbox hacks to allow content within to scroll correctly */}
          <div className="flex-grow h-0 min-h-0">
             {/* ChatPanel should handle its own internal scrolling */}
             <ChatPanel onNewSuggestions={setSuggestions} />
          </div>

          {/* Mobile Results Canvas Container (Horizontal Scroll) */}
          {/* Displayed only on small screens (block) and hidden on medium+ (md:hidden) */}
          {/* flex-shrink-0 prevents it from shrinking */}
          {/* Added border and background for visual separation */}
          <div className="block md:hidden flex-shrink-0 border-t-4 border-black bg-green-100">
             {/* Pass the results state and specify horizontal layout */}
             <ResultsCanvas
                suggestedExperiences={suggestions} // Use the correct prop name from ResultsCanvas.txt
                isLoading={isLoadingDefaults}
                layout="horizontal"
             />
          </div>
        </div>

        {/* Desktop Results Canvas Container (Vertical Scroll) */}
        {/* Hidden on small screens (hidden), displayed as a block on medium+ (md:block) */}
        {/* flex-shrink-0 prevents shrinking. Takes remaining width on desktop */}
        {/* Full height of the parent row */}
        <div className="hidden md:block flex-shrink-0 md:w-2/5 lg:w-1/3 h-full">
           {/* ResultsCanvas handles its own border and background in vertical mode */}
           {/* Pass the results state and specify vertical layout */}
           <ResultsCanvas
              suggestedExperiences={suggestions} // Use the correct prop name
              isLoading={isLoadingDefaults}
              layout="vertical"
            />
        </div>

      </div>
    </div>
    </div>
  );
}
