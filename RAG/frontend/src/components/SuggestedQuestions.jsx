import React, { useState, useEffect } from "react";

const SuggestedQuestions = ({ suggestedQuestions, setShowChat, sendMessage }) => {
  const fullText = "Come posso aiutarti oggi?";
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let currentIndex = 1;
    const typingSpeed = 100;
    let isCancelled = false;

    const typeText = () => {
      if (isCancelled) return;

      setDisplayedText(fullText.substring(0, currentIndex));
      if (currentIndex < fullText.length) {
        currentIndex++;
        setTimeout(typeText, typingSpeed);
      }
    };

    typeText();
    return () => { isCancelled = true; };
  }, []);

  return (
    <div className="flex flex-col items-center mt-10 text-center w-full">
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-8 self-center">
        {displayedText}
      </h2>
      <div className="flex flex-wrap justify-center gap-4 sm:gap-6 md:gap-8 w-full">
        {suggestedQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => {
              setShowChat(true);
              sendMessage(question);
            }}
            className="flex items-center space-x-2 px-4 sm:px-6 py-3 sm:py-4 border border-[#e5e7eb] rounded-xl shadow-lg text-base sm:text-lg font-semibold text-gray-800 bg-white hover:bg-[#f1f5f9] transition focus:outline-none focus:ring-2 focus:ring-[#6366f1]"
            style={{ minWidth: "200px", maxWidth: "90vw", wordBreak: "break-word" }}
          >
            <span>{question}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedQuestions;
