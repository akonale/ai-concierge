// frontend/src/app/page.tsx (Example using App Router)
// frontend/src/app/page.tsx (Example using App Router)
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import ChatPanel from '@/components/ChatPanel';
import ResultsCanvas from '@/components/ResultsCanvas'; // Import the new component

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-white"> {/* Changed background to white for consistency */}
      <Navbar />
      <div className="flex flex-grow overflow-hidden"> {/* Main layout container */}
        {/* Sidebar: Width is controlled internally by the component */}
        <Sidebar />
        {/* Chat Panel: Takes up the central flexible space */}
        <div className="flex-grow">
          <ChatPanel />
        </div>
        {/* Results Canvas: Fixed width on the right */}
        <div className="w-1/4 flex-shrink-0"> {/* Adjust width as needed (e.g., w-96) */}
          <ResultsCanvas />
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
