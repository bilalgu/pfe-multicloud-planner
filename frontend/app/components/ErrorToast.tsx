'use client';

interface ErrorToastProps {
  message: string;
  onClose: () => void;
}

export default function ErrorToast({ message, onClose }: ErrorToastProps) {
  return (
    <div className="fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center gap-4 animate-slide-in">
      <div className="flex-1">
        <strong>Erreur :</strong> {message}
      </div>
      <button
        onClick={onClose}
        className="text-white hover:text-red-200 font-bold text-xl"
      >
        ×
      </button>
    </div>
  );
}
