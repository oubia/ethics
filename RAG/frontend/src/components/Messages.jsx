import React from 'react';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

const Message = ({ msg, isUser, isAssistantTyping }) => {
  const FormattedText = ({ children }) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkBreaks]}
      components={{
        h1: ({ node, ...props }) => (
          <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-xl font-semibold mt-4 mb-2" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-lg font-medium mt-3 mb-1" {...props} />
        ),
        p: ({ node, ...props }) => (
          <p className="leading-relaxed mb-2" {...props} />
        ),
        ul: ({ node, ...props }) => (
          <ul className="list-disc pl-6 space-y-1" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal pl-6 space-y-1" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="leading-relaxed" {...props} />
        ),
        strong: ({ node, ...props }) => (
          <strong className="font-semibold" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote
            className="border-l-4 border-gray-300 italic pl-4 my-2"
            {...props}
          />
        ),
        hr: () => <hr className="my-4 border-t border-gray-300" />,
      }}
    >
      {children}
    </ReactMarkdown>
  );

  return (
    <div className="my-3">
      {!isUser && msg.selectedapproach && (
        <div className="flex items-center justify-center mb-2">
          <span className="flex-grow border-t border-gray-300 mx-4"></span>
          <span className="italic text-gray-400 text-xs">
            {msg.selectedapproach} + {msg.selectedChunkSize} + {msg.selectedapproachRetriever}
          </span>
          <span className="flex-grow border-t border-gray-300 mx-4"></span>
        </div>
      )}
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div
          className={`relative max-w-3xl px-6 py-3 rounded-xl shadow
            ${isUser
              ? 'bg-[#6366f1] text-white rounded-br-none'
              : 'bg-[#f3f6fd] text-gray-900 rounded-bl-none'
            }`
          }
        >
          {isAssistantTyping ? (
            <div className="flex items-center">
              <div className="loading-spinner"></div>
              <span className="ml-2 text-gray-400">Sto pensando...</span>
            </div>
          ) : (
            <div>
              <FormattedText>{msg.content}</FormattedText>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

Message.propTypes = {
  msg: PropTypes.shape({
    role: PropTypes.string.isRequired,
    content: PropTypes.string,
  }).isRequired,
  isUser: PropTypes.bool.isRequired,
  isAssistantTyping: PropTypes.bool.isRequired,
};

export default Message;
