'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mb-4"></div>
      <p className="text-gray-600 text-lg">Génération en cours...</p>
      <p className="text-gray-500 text-sm mt-2">Cela peut prendre quelques secondes</p>
    </div>
  );
}
