import React, { useState, useRef, useEffect, useCallback } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';

import { FaArrowLeft, FaArrowDown, FaRegStopCircle } from "react-icons/fa";
import { RiVoiceprintLine } from "react-icons/ri";

import SuggestedQuestions from './components/SuggestedQuestions';
import Message from './components/Messages';
import PermissionAlert from "./components/PermissionAlert";
import FormattedText from "./components/FormattedText";
import SourceFilesPanel from './components/LeftPannel';
const chatApiUrl = process.env.REACT_APP_BASE_URL;

const App = () => {
  const [messageHistory, setMessageHistory] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [showSuggestedQuestions, setShowSuggestedQuestions] = useState(true);
  const [showScrollToBottom, setShowScrollToBottom] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [hasMicrophonePermission, setHasMicrophonePermission] = useState(false);
  const [isPermissionAlertVisible, setIsPermissionAlertVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [docPanelOpen, setDocPanelOpen] = useState(true);
  const [sourceFiles, setSourceFiles] = useState([]);

  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const microphoneStreamRef = useRef(null);

  const disabled = loading || input.trim() === '';
  const suggestedQuestions = [
    "Quale legge ha istituito il Ministero del Turismo?",
    'Cosa prevede il comma 3 dell’articolo 6 del Decreto-Legge 1° marzo 2021, n. 22?',
    "Cosa stabilisce il DPCM del 20 maggio 2021, n. 102?",
    "Cos’è il Regolamento (UE) n. 2021/241 del 12 febbraio 2021?",
    'Quando è stato approvato il PNRR italiano dal Consiglio ECOFIN?',
  ];
  const [selectedapproach, setselectedapproach] = useState('Native-chunking');
  const approach = ['Native-chunking', 'Late-chunking'];
  const [selectedChunkSize, setselectedChunkSize] = useState('750');
  const chunksize = ['750', "250"];
  const [selectedapproachRetriever, setselectedapproachRetriever] = useState('Hybrid-fusion');
  const retrieverOptions = ['Hybrid-fusion', 'Similarity-research', 'Contextual-Compression', 'Answer-With-Multiquery'];

  const handleLLMChange = (e) => setselectedapproach(e.target.value);
  const handleVectordbChange = (e) => setselectedChunkSize(e.target.value);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messageHistory]);
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 160);
    textarea.style.height = `${newHeight}px`;
    textarea.style.overflowY = newHeight === 160 ? 'auto' : 'hidden';
  }, []);
  useEffect(() => { adjustTextareaHeight(); }, [input, adjustTextareaHeight]);
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
  }, [messageHistory]);

    const handleStreamResponse = async (response) => {
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Server error:", errorText);
      setError(`Server error: ${response.status}`);
      setLoading(false);
      return;
    }

    if (!response.body) {
      setError("Stream error: no response body");
      setLoading(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let newMessage = "";
    let foundSources = false;
    let done = false;

    setMessageHistory((prev) => [
      ...prev,
      { role: "assistant", content: "", selectedapproach, selectedChunkSize, selectedapproachRetriever }
    ]);

    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;

      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.trim().startsWith("data:")) {
            try {
              const jsonString = line.trim().substring(5);
              const parsedChunk = JSON.parse(jsonString);

              if (parsedChunk.response) {
                newMessage += parsedChunk.response;
                setMessageHistory((prev) => {
                  const updated = [...prev];
                  updated[updated.length - 1].content = newMessage;
                  return updated;
                });
              }
              if (parsedChunk.sources) {
                setSourceFiles(parsedChunk.sources);
                foundSources = true;
              }
            } catch (parseError) {
              console.error("Failed to parse JSON chunk:", parseError, line);
            }
          }
        }
      }
    }

    setLoading(false);
  };

  const sendMessage = async (message = input) => {
    if (!message?.trim()) return;

    setShowSuggestedQuestions(false);
    setShowChat(true);
    setLoading(true);
    setError(null);

    setMessageHistory((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setSourceFiles([]);

    try {
      const response = await fetch(`http://127.0.0.1:8000/chat/`, {
        headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
        method: "POST",
        body: JSON.stringify({ 
          content: message,
          selectedapproach:selectedapproach,
          selectedChunkSize:selectedChunkSize,
          selectedapproachRetriever: selectedapproachRetriever,
        }),
        // credentials: "include",
      });
      await handleStreamResponse(response);
    } catch (networkError) {
      console.error("Network error:", networkError);
      setError("Network error");
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleDeleteChat = async () => {
    try {
      const response = await fetch(`${chatApiUrl}/delete_chat/`, {
        method: 'DELETE',
        // credentials: 'include',
      });

      if (response.ok) {
        setMessageHistory([]);
        setSuccess(true);
        setTimeout(() => setSuccess(false), 2000);
        setShowSuggestedQuestions(true);
        setShowChat(false);
      } else {
        setError('Failed to delete chat history');
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
      setError('Network error');
    }
  };

  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    setShowScrollToBottom(!(scrollHeight - scrollTop === clientHeight));
  };

  const scrollToBottom = () => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
  };

  const findLastIndex = (array, predicate) => {
    for (let i = array.length - 1; i >= 0; i--) {
      if (predicate(array[i])) return i;
    }
    return -1;
  };

  const handleAudioResponse = async (response) => {
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Server error:", errorText);
      setError(`Server error: ${response.status}`);
      setLoading(false);
      return;
    }

    if (!response.body) {
      setError("Stream error: no response body");
      setLoading(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let done = false;
    let transcriptionText = "";
    let assistantMessage = "";

    setMessageHistory((prev) => [
      ...prev,
      { role: "user", content: "" },
      { role: "assistant", content: "" },
    ]);

    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;

      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.trim().startsWith("data:")) {
            try {
              const jsonString = line.trim().substring(5);
              const parsedChunk = JSON.parse(jsonString);

              if (parsedChunk.type === "transcription") {
                transcriptionText += parsedChunk.response;
                setMessageHistory((prev) => {
                  const updated = [...prev];
                  const lastUserIndex = findLastIndex(updated, (msg) => msg.role === "user");
                  if (lastUserIndex !== -1) {
                    updated[lastUserIndex].content = transcriptionText;
                  }
                  return updated;
                });
              }

              if (parsedChunk.type === "assistant") {
                assistantMessage += parsedChunk.response;
                setMessageHistory((prev) => {
                  const updated = [...prev];
                  const lastAssistantIndex = findLastIndex(updated, (msg) => msg.role === "assistant");
                  if (lastAssistantIndex !== -1) {
                    updated[lastAssistantIndex].content = assistantMessage;
                  }
                  return updated;
                });
              }
            } catch (parseError) {
              console.error("Failed to parse JSON chunk:", parseError, line);
            }
          }
        }
      }
    }

    setLoading(false);
    setIsSubmitting(false);
  };

  const sendAudioToBackend = async (audioBlob) => {
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.wav");

    setShowSuggestedQuestions(false);
    setShowChat(true);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/process_audio/`, {
        method: "POST",
        mode: "no-cors",
        body: formData,
      });

      await handleAudioResponse(response);
    } catch (sendError) {
      console.error("Error sending audio to backend:", sendError);
      setError("Failed to process audio. Please try again.");
      setLoading(false);
      setIsSubmitting(false);
    }
  };

  const initializeMediaRecorder = (stream) => {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
      sendAudioToBackend(audioBlob);
    };

    mediaRecorder.start();
    setIsListening(true);
  };

  const startListening = async () => {
    try {
      if (hasMicrophonePermission && microphoneStreamRef.current) {
        initializeMediaRecorder(microphoneStreamRef.current);
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasMicrophonePermission(true);
      microphoneStreamRef.current = stream;
      initializeMediaRecorder(stream);
    } catch (error) {
      console.error("Microphone access denied or error occurred:", error);
      setIsPermissionAlertVisible(true);
    }
  };

  const handleAllow = (stream) => {
    setIsPermissionAlertVisible(false);
    microphoneStreamRef.current = stream;
    setHasMicrophonePermission(true);
    initializeMediaRecorder(stream);
  };

  const handleDeny = () => {
    setIsPermissionAlertVisible(false);
    console.error("Microphone permission denied.");
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setIsListening(false);
    setIsSubmitting(true);
  };

  useEffect(() => {
    console.log("sourceFiles:", sourceFiles);
  }, [sourceFiles]);
  // ---- LAYOUT ----
  return (
    <Router>
<div className="min-h-screen w-full flex flex-col md:flex-row justify-center items-stretch bg-white py-2 md:py-10 px-1 md:px-2 gap-2 md:gap-6 relative overflow-hidden">
    {/* Left Panel */}
    <div className="flex-shrink-0  hidden lg:block">
      <h2 className="text-md font-bold text-[#6366f1]">Fonti (Files recuperati)</h2>
      {sourceFiles.length > 0 && (
        <SourceFilesPanel sourceFiles={sourceFiles} onClose={() => setSourceFiles([])} />
      )}
      
      {docPanelOpen && (
        <div className={`transition-all duration-300 w-72 md:w-[22rem] opacity-100 overflow-hidden`}>
          <div className="glass-card h-[28rem] md:h-[44rem] flex flex-col relative shadow-lg transition-all">
            <div className="mt-6 overflow-auto flex-1">
              <div className="p-2">
              </div>
            </div>
          </div>
        </div>
      )}
    </div>


  {/* --- CENTER: Chat --- */}
  <div className="flex-1 max-w-full md:max-w-3xl lg:max-w-5xl min-w-0 flex flex-col justify-between relative bg-transparent">
    <div className="flex-1 flex flex-col relative bottom-0">
      <div className="w-full animate-glass-in  flex flex-col flex-1 relative" style={{ minHeight: '68vh', paddingBottom: '0' }}>
        {!showSuggestedQuestions && (
          <button
            onClick={() => {
              setShowSuggestedQuestions(true);
              setShowChat(false);
            }}
            className="absolute top-4 left-4 flex items-center px-2 py-2 rounded-md shadow bg-white text-[#6366f1] hover:bg-[#6366f1] hover:text-white transition z-10"
            title="Torna alle domande suggerite"
          >
            <FaArrowLeft className="text-lg" />
          </button>
        )}
        {isPermissionAlertVisible && (
          <PermissionAlert onAllow={handleAllow} onDeny={handleDeny} />
        )}
        {showSuggestedQuestions && !showChat ? (
          <SuggestedQuestions
            suggestedQuestions={suggestedQuestions}
            setShowChat={setShowChat}
            sendMessage={(msg) => { sendMessage(msg); setShowChat(true); }}
          />
        ) : (
          <div
            className="flex flex-col gap-4 px-1 md:px-3 py-2 h-[85vh] md:h-[85vh] overflow-y-auto hide-scrollbar"
            ref={messagesContainerRef}
            onScroll={handleScroll}
          >
            {messageHistory.map((msg, index) => (
              <Message
                key={index}
                msg={msg}
                isUser={msg.role === 'user'}
                isAssistantTyping={msg.role === 'assistant' && !msg.content && loading && index === messageHistory.length - 1}
                className={msg.role === 'user' ? 'msg-user' : 'msg-assistant'}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </div>

    <div className="fixed left-1/2 bottom-2 md:bottom-6 transform -translate-x-1/2 w-[98vw] md:w-[46rem] lg:w-[52rem] max-w-[98vw] z-30 px-1 md:px-0">
      {error && (
        <div className=" animate-fadeIn mt-3 p-2 rounded-lg bg-[#fca5a5] text-white font-medium shadow">{ <FormattedText>{error}</FormattedText>}</div>
      )}
      {success && (
        <div className="mt-3 p-2 rounded-lg bg-[#bbf7d0] text-[#047857] font-medium shadow">Chat history has been deleted</div>
      )}
      <div className="flex items-end px-2 md:px-4 py-2 ">
        <textarea
          ref={textareaRef}
          value={input || ''}
          className="styled-textarea w-full min-h-[2.5rem] max-h-40"
          onChange={e => { setInput(e.target.value); setError(null); }}
          onKeyDown={handleKeyDown}
          rows="1"
          placeholder="Scrivi un messaggio..."
          disabled={loading}
        />
        {loading ? (
          <div className="loading-spinner mx-2"></div>
        ) : (
          <>
            <button
              className="btn-primary ml-2"
              onClick={() => sendMessage()}
              disabled={disabled}
            >
              Invia
            </button>
            <button
              className="btn-primary bg-gradient-to-r from-[#22d3ee] to-[#6366f1] ml-2"
              onClick={isListening ? handleStopRecording : startListening}
              disabled={isSubmitting}
            >
              {isListening ? <FaRegStopCircle size={17} /> : <RiVoiceprintLine size={17} />}
            </button>
          </>
        )}
      </div>
      

    </div>
  </div>

  {/* --- RIGHT: Settings Panel --- */}
  <div className="hidden lg:block w-[20rem] ml-0 md:ml-5 flex-shrink-0">
    <div className="fixed top-12 right-2 lg:right-8 w-72 z-30 glass-card animate-glass-in">
      {/* ... Settings as before ... */}
      <h2 className="text-lg font-bold mb-2 text-[#6366f1]">Seleziona Approccio</h2>
      {approach.map((llm) => (
        <label key={llm} className="selector-card flex items-center space-x-2">
          <input
            type="radio"
            name="llm"
            value={llm}
            checked={selectedapproach === llm}
            onChange={handleLLMChange}
            className="accent-[#6366f1]"
          />
          <span>{llm}</span>
        </label>
      ))}
      <h2 className="text-lg font-bold mt-4 mb-2 text-[#38bdf8]">Chunk Size</h2>
      {chunksize.map((vector) => (
        <label key={vector} className="selector-card flex items-center space-x-2">
          <input
            type="radio"
            name="vector"
            value={vector}
            checked={selectedChunkSize === vector}
            onChange={handleVectordbChange}
            className="accent-[#38bdf8]"
          />
          <span>{vector}</span>
        </label>
      ))}
      <h2 className="text-lg font-bold mt-4 mb-2 text-[#14b8a6]">Retriever</h2>
      {retrieverOptions.map((retriever) => (
        <label key={retriever} className="selector-card flex items-center space-x-2">
          <input
            type="radio"
            name="retriever"
            value={retriever}
            checked={selectedapproachRetriever === retriever}
            onChange={e => setselectedapproachRetriever(e.target.value)}
            className="accent-[#14b8a6]"
          />
          <span>{retriever}</span>
        </label>
      ))}
    </div>
  </div>
</div>

    </Router>
  );
};

export default App;
