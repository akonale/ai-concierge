// frontend/src/components/ResultsCanvas.tsx
import React from 'react';
// Assuming ExperienceCardData is defined in @/types or similar
import { ExperienceCardData } from '@/types';

// --- Experience Card Component ---
interface ExperienceCardProps {
  experience: ExperienceCardData;
  layout: 'horizontal' | 'vertical'; // Added layout prop
}

const ExperienceCard: React.FC<ExperienceCardProps> = ({ experience, layout }) => {
  // Default image if none provided from your ResultCanvas.txt
  const defaultImageUrl = "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1999&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"; // Placeholder Yoga image
  const imageUrl = experience.image_url || defaultImageUrl;

  // Function to safely render optional fields (from your ResultCanvas.txt)
  const renderOptionalField = (label: string, value: string | null | undefined) => {
    // Reduced bottom margin for tighter spacing
    return value ? <p className="text-xs text-gray-700 mb-0.5"><span className="font-semibold">{label}:</span> {value}</p> : null;
  };

  // Base classes from your ResultCanvas.txt, adjusted padding
  const baseClasses = "bg-white border-2 border-black p-2 md:p-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex flex-col";
  // Layout specific classes for responsiveness
  const layoutClasses = layout === 'horizontal'
    // Fixed width for horizontal scroll, responsive adjustments, margin-right for spacing
    ? "w-48 sm:w-56 md:w-64 flex-shrink-0 mr-3"
    // Full width for vertical scroll, margin-bottom for spacing
    : "w-full mb-4";

  return (
    // Combine base and layout-specific classes
    <div className={`${baseClasses} ${layoutClasses}`}>
      {/* Image: Adjusted height based on layout */}
      <img
        src={imageUrl}
        alt={experience.name || 'Experience image'}
        className={`w-full object-cover border-b-2 border-black mb-2 ${layout === 'horizontal' ? 'h-24 sm:h-28' : 'h-32'}`} // Responsive height
        onError={(e) => { (e.target as HTMLImageElement).src = defaultImageUrl; }} // Fallback on error
      />
      {/* Content Area */}
      <div className="flex-grow mb-1"> {/* Reduced bottom margin */}
        {/* Responsive text size and line clamping */}
        <h3 className="text-sm md:text-md font-bold text-black mb-1 line-clamp-2">{experience.name}</h3>
        {experience.description && (
          // Adjust line clamping based on layout
          <p className={`text-xs md:text-sm text-black mb-1 ${layout === 'horizontal' ? 'line-clamp-2' : 'line-clamp-3'}`}>{experience.description}</p>
        )}
        {/* Render optional fields */}
        {renderOptionalField("Price", experience.price)}
        {renderOptionalField("Duration", experience.duration)}
        {renderOptionalField("Type", experience.type)}
      </div>
      {/* Link/Button */}
      {experience.url && (
        <a
          href={experience.url}
          target="_blank"
          rel="noopener noreferrer"
          // Use auto margin top to push button down, responsive text/padding
          className="mt-auto inline-block bg-black text-white text-center text-xs md:text-sm font-bold py-1 px-2 border-2 border-black hover:bg-gray-800 rounded-none"
        >
          More Info
        </a>
      )}
    </div>
  );
};


// --- Updated ResultsCanvas Component ---
interface ResultsCanvasProps {
  suggestedExperiences: ExperienceCardData[] | null; // Prop name from your ChatPanel.txt
  isLoading: boolean;
  layout: 'horizontal' | 'vertical'; // Prop to control layout
}

const ResultsCanvas: React.FC<ResultsCanvasProps> = ({ suggestedExperiences, isLoading, layout }) => {
  // Use the passed experiences directly
  const topSuggestions = !isLoading && Array.isArray(suggestedExperiences) ? suggestedExperiences : [];

  // Container classes based on layout
  const containerBaseClasses = "h-full bg-green-100"; // Base height
  // Horizontal: Flex row, horizontal scroll, specific height, padding
  const horizontalContainerClasses = "flex overflow-x-auto space-x-0 p-3 h-56 sm:h-64 bg-green-100"; // Added fixed height, padding
  // Vertical: Vertical scroll, padding, border (applied by parent in page.tsx)
  const verticalContainerClasses = "overflow-y-auto p-2 md:p-4 bg-green-100";

  // Combine classes based on the layout prop
  const containerClasses = layout === 'horizontal'
    ? `${containerBaseClasses} ${horizontalContainerClasses}`
    : `${containerBaseClasses} ${verticalContainerClasses}`;

  return (
    // Use calculated container classes
    // Background color applied by parent div in page.tsx for horizontal layout
    // Border applied by parent div in page.tsx for vertical layout
    <aside className={containerClasses}>
      {/* Title only shown in vertical layout (desktop) */}
      {/* Added sticky positioning and background for better scrolling */}
      {layout === 'vertical' && (
         <h2 className="text-lg md:text-xl font-bold mb-4 text-black sticky top-0 py-1 z-10">Suggestions</h2>
      )}

      {/* Loading State */}
      {isLoading ? (
        // Center loading indicator, adjust height based on layout
        <div className={`flex justify-center items-center ${layout === 'vertical' ? 'h-full' : 'h-full w-full min-w-[100px]'}`}> {/* Min width for horizontal */}
           <p className="text-black italic animate-pulse">Loading suggestions...</p>
        </div>
      ) : topSuggestions.length > 0 ? (
        // Render Cards: Use a flex container only for horizontal layout
        <div className={layout === 'horizontal' ? 'flex h-full items-start' : ''}>
          {topSuggestions.map((exp) => (
            <ExperienceCard key={exp.id} experience={exp} layout={layout} />
          ))}
          {/* Add padding element at the end of horizontal scroll for better spacing */}
          {layout === 'horizontal' && <div className="flex-shrink-0 w-3"></div>}
        </div>
      ) : (
         // No Suggestions Message: Center it, adjust height based on layout
         <div className={`flex justify-center items-center ${layout === 'vertical' ? 'h-full' : 'h-full w-full min-w-[200px]'}`}> {/* Min width for horizontal */}
            <p className="text-black italic text-sm md:text-base text-center px-2">No specific suggestions found.</p>
         </div>
      )}
    </aside>
  );
};

export default ResultsCanvas;
