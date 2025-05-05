// frontend/src/components/ResultsCanvas.tsx
import React from 'react';
import { ExperienceCardData } from '@/types'; // Import the type

// --- New Component for Rendering a Single Experience Card ---
interface ExperienceCardProps {
  experience: ExperienceCardData;
}

const ExperienceCard: React.FC<ExperienceCardProps> = ({ experience }) => {
  // Default image if none provided
  const defaultImageUrl = "https://images.unsplash.com/photo-1506126613408-eca07ce68773?q=80&w=1999&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"; // Placeholder Yoga image
  const imageUrl = experience.image_url || defaultImageUrl;

  // Function to safely render optional fields
  const renderOptionalField = (label: string, value: string | null | undefined) => {
    return value ? <p className="text-xs text-gray-700"><span className="font-semibold">{label}:</span> {value}</p> : null;
  };

  return (
    <div className="bg-white border-2 border-black p-3 mb-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex flex-col">
      {/* Image */}
      <img
        src={imageUrl}
        alt={experience.name || 'Experience image'}
        className="w-full h-32 object-cover border-b-2 border-black mb-2" // Consistent styling
        onError={(e) => { (e.target as HTMLImageElement).src = defaultImageUrl; }} // Fallback on error
      />
      {/* Content */}
      <div className="flex-grow">
        <h3 className="text-md font-bold text-black mb-1">{experience.name}</h3>
        {experience.description && (
          <p className="text-sm text-black mb-2">{experience.description}</p>
        )}
        {/* Optional details */}
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
          className="mt-2 inline-block bg-black text-white text-center text-sm font-bold py-1 px-3 border-2 border-black hover:bg-gray-800 rounded-none" // Neo-brutalist button
        >
          More Info
        </a>
      )}
    </div>
  );
};


// --- Updated ResultsCanvas Component ---
interface ResultsCanvasProps {
  suggestedExperiences: ExperienceCardData[] | null;
}

const ResultsCanvas: React.FC<ResultsCanvasProps> = ({ suggestedExperiences }) => {
  // Get top 5 suggestions
  const topSuggestions = suggestedExperiences ? suggestedExperiences.slice(0, 5) : [];

  return (
    // Canvas container: Light green background, black left border, padding, scrollable
    <aside className="h-full bg-green-100 border-l-4 border-black p-4 overflow-y-auto">
      <h2 className="text-xl font-bold mb-4 text-black">Suggestions</h2> {/* Changed title */}

      {/* Render suggestions or a placeholder message */}
      {topSuggestions.length > 0 ? (
        topSuggestions.map((exp) => (
          <ExperienceCard key={exp.id} experience={exp} />
        ))
      ) : (
        <p className="text-black italic">No specific suggestions found based on the current conversation.</p>
      )}
    </aside>
  );
};

export default ResultsCanvas;
