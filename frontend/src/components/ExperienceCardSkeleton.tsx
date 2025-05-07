// frontend/src/components/ExperienceCardSkeleton.tsx
import React from 'react';

interface ExperienceCardSkeletonProps {
  layout: 'horizontal' | 'vertical'; // To match the layout prop
}

const ExperienceCardSkeleton: React.FC<ExperienceCardSkeletonProps> = ({ layout }) => {
  // Base classes mimicking ExperienceCard structure + pulse animation
  const baseClasses = "bg-white border-2 border-gray-300 p-2 md:p-3 shadow-md flex flex-col animate-pulse";
  // Layout specific classes mimicking ExperienceCard
  const layoutClasses = layout === 'horizontal'
    ? "w-48 sm:w-56 md:w-64 flex-shrink-0 mr-3" // Fixed width for horizontal scroll
    : "w-full mb-4"; // Full width for vertical scroll

  return (
    <div className={`${baseClasses} ${layoutClasses}`}>
      {/* Image Placeholder */}
      <div className={`w-full bg-gray-300 border-b-2 border-gray-300 mb-2 ${layout === 'horizontal' ? 'h-24 sm:h-28' : 'h-32'}`}></div>

      {/* Content Placeholder */}
      <div className="flex-grow mb-1 space-y-2">
        {/* Title Placeholder */}
        <div className="h-4 bg-gray-300 rounded w-3/4"></div>
        {/* Description Placeholder Lines */}
        <div className="h-3 bg-gray-300 rounded w-full"></div>
        <div className="h-3 bg-gray-300 rounded w-5/6"></div>
        {/* Optional Details Placeholders */}
        <div className="h-2 bg-gray-300 rounded w-1/2 mt-1"></div>
        <div className="h-2 bg-gray-300 rounded w-1/3"></div>
      </div>
      {/* Button Placeholder */}
      <div className="mt-auto h-7 bg-gray-300 rounded w-1/2 self-start"></div>
    </div>
  );
};

export default ExperienceCardSkeleton;
