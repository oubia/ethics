import React, { useState } from "react";
import { FaMicrophone } from "react-icons/fa";

const PermissionAlert = ({ onAllow, onDeny }) => {
  const [visible, setVisible] = useState(true);

  const handleAllow = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setVisible(false);
      onAllow(stream);
    } catch (error) {
      console.error("Microphone access denied by user or browser settings.", error);
      setVisible(false);
      onDeny(); 
    }
  };

  const handleDeny = () => {
    setVisible(false);
    onDeny();
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 border border-[#e5e7eb] w-[92vw] max-w-sm">
        <div className="flex items-center justify-center mb-4">
          <FaMicrophone size={36} className="text-[#6366f1]" />
        </div>
        <h2 className="text-xl font-bold text-gray-800 text-center mb-2">
          Microphone Permission
        </h2>
        <p className="text-gray-600 text-center mb-6">
          We need your permission to access the microphone for recording your voice.
        </p>
        <div className="flex justify-center space-x-4">
          <button
            onClick={handleAllow}
            className="btn-primary w-28"
          >
            Allow
          </button>
          <button
            onClick={handleDeny}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-xl font-semibold shadow transition hover:bg-gray-300 w-28"
          >
            Deny
          </button>
        </div>
      </div>
    </div>
  );
};

export default PermissionAlert;
