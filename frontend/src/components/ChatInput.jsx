import { useState } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';

const ChatInput = ({ onSubmit, isLoading, placeholder }) => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto">
      <div className={`relative group transition-all duration-300 ${isFocused ? 'scale-[1.02]' : ''}`}>
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-lg opacity-20 group-hover:opacity-30 transition-opacity"></div>
        <div className="relative flex items-center bg-white/90 backdrop-blur-sm border border-gray-200 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="pl-4">
            <Sparkles className={`w-5 h-5 text-blue-600 transition-colors ${isFocused ? 'text-purple-600' : ''}`} />
          </div>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1 px-4 py-4 text-gray-900 bg-transparent placeholder-gray-500 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={`mr-2 p-3 text-white rounded-xl transition-all duration-200 ${
              input.trim() && !isLoading
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
      
      {/* Suggested prompts */}
      {!input && !isLoading && (
        <div className="mt-4 flex flex-wrap gap-2 justify-center">
          {[
            "Improving transformer efficiency for long sequences",
            "Novel approaches to few-shot learning",
            "Quantum machine learning applications"
          ].map((suggestion, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setInput(suggestion)}
              className="px-4 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-full hover:bg-gray-50 hover:border-gray-300 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </form>
  );
};

export default ChatInput;
