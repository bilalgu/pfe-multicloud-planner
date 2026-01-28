'use client';

interface SuccessToastProps {
  message: string;
  onClose: () => void;
}

export default function SuccessToast({ message, onClose }: SuccessToastProps) {
  return (
    <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center gap-4 animate-slide-in">
      <div className="flex-1">
        <strong>Succès :</strong> {message}
      </div>
      <button
        onClick={onClose}
        className="text-white hover:text-green-200 font-bold text-xl"
      >
        ×
      </button>
    </div>
  );
}
