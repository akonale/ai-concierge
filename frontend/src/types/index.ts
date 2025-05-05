// frontend/src/types/index.ts

/**
 * Defines the structured data for a single experience card
 * mirroring the backend ExperienceCardData model.
 */
export interface ExperienceCardData {
  id: string;
  name: string;
  description?: string | null;
  image_url?: string | null; // Assuming HttpUrl from backend is represented as string
  price?: string | null;
  duration?: string | null;
  type?: string | null;
  url?: string | null;
  // Add other fields if they exist in the backend model and are needed
}
