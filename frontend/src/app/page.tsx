// frontend/src/app/page.tsx (Example using App Router)
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import ChatPanel from '@/components/ChatPanel';

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-gray-200">
      <Navbar />
      <div className="flex flex-grow overflow-hidden"> {/* Ensure inner flex container grows */}
        <div className="w-1/5 flex-shrink-0"> {/* Fixed width sidebar */}
          <Sidebar />
        </div>
        <div className="flex-grow"> {/* Main content area takes remaining space */}
          <ChatPanel />
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