'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface OnboardingChatProps {
  tenantId: string;
  practiceName?: string;
  email?: string;
  onComplete?: (clientId: string, collectedData: any) => void;
}

export default function OnboardingChat({
  tenantId,
  practiceName,
  email,
  onComplete,
}: OnboardingChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [clientId, setClientId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [totalQuestions, setTotalQuestions] = useState(48);
  const [isCompleted, setIsCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAutoFilling, setIsAutoFilling] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Start onboarding session
  useEffect(() => {
    const startOnboarding = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`${API_URL}/onboarding/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tenant_id: tenantId,
            practice_name: practiceName || 'New Practice',
            email: email || 'contact@practice.com',
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to start onboarding: ${response.statusText}`);
        }

        const data = await response.json();
        
        setSessionId(data.session_id);
        setClientId(data.client_id);
        setCurrentStep(data.current_step);
        setCurrentStage(data.current_stage);
        setTotalQuestions(data.total_questions);
        
        // Check if there's history (resuming session)
        if (data.history && data.history.length > 0) {
          // Load full conversation history
          const historyMessages = data.history.map((msg: any) => ({
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(),
          }));
          setMessages(historyMessages);
        } else {
          // New session - Add first question as assistant message
          setMessages([
            {
              role: 'assistant',
              content: data.message,
              timestamp: new Date(),
            },
          ]);
        }
      } catch (err) {
        console.error('Error starting onboarding:', err);
        setError(err instanceof Error ? err.message : 'Failed to start onboarding');
      } finally {
        setIsLoading(false);
      }
    };

    startOnboarding();
  }, [tenantId, practiceName, email]);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || isLoading || isStreaming) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setError(null);

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userMessage, timestamp: new Date() },
    ]);

    try {
      const response = await fetch(`${API_URL}/onboarding/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }

      const data = await response.json();

      // Update state
      setCurrentStep(data.current_step);
      setCurrentStage(data.current_stage);
      setIsCompleted(data.is_completed);

      setIsLoading(false);

      // Stream bot messages with typing effect
      const messagesToStream = data.bot_messages && data.bot_messages.length > 0 
        ? data.bot_messages 
        : [data.bot_message];

      for (const messageContent of messagesToStream) {
        await streamMessage(messageContent);
      }

      // If completed, call onComplete callback
      if (data.is_completed && onComplete && clientId) {
        onComplete(clientId, data.collected_data);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
      
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Sorry, there was an error processing your response. Please try again.',
          timestamp: new Date(),
        },
      ]);
      setIsLoading(false);
    } finally {
      inputRef.current?.focus();
    }
  };

  // Stream message with typing effect
  const streamMessage = async (content: string): Promise<void> => {
    return new Promise((resolve) => {
      setIsStreaming(true);
      
      // Add empty message that we'll populate
      const messageIndex = messages.length;
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        },
      ]);

      let currentIndex = 0;
      const words = content.split(' ');
      
      // Stream word by word for smoother effect
      const interval = setInterval(() => {
        if (currentIndex < words.length) {
          const newContent = words.slice(0, currentIndex + 1).join(' ');
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              content: newContent,
            };
            return updated;
          });
          currentIndex++;
        } else {
          clearInterval(interval);
          setIsStreaming(false);
          resolve();
        }
      }, 30); // 30ms per word for smooth typing effect
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Auto-fill with AI-generated response
  const autoFillResponse = async () => {
    if (!sessionId || isLoading || isAutoFilling || isCompleted) return;

    setIsAutoFilling(true);
    setError(null);

    try {
      // Get the last bot message (current question)
      const lastBotMessage = [...messages].reverse().find(m => m.role === 'assistant');
      if (!lastBotMessage) {
        throw new Error('No question found');
      }

      const currentQuestion = lastBotMessage.content;

      // Generate a realistic answer using OpenAI
      const response = await fetch(`${API_URL}/onboarding/generate-answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentQuestion,
          practice_name: practiceName || 'Medical Practice',
          context: {
            current_step: currentStep,
            stage: currentStage,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate answer');
      }

      const data = await response.json();
      const generatedAnswer = data.answer;

      // Set the generated answer in the input
      setInput(generatedAnswer);
      
      // Optional: Auto-send after a short delay
      setTimeout(() => {
        setInput(generatedAnswer);
        inputRef.current?.focus();
      }, 100);

    } catch (err) {
      console.error('Error generating answer:', err);
      setError('Failed to generate answer. Please type manually.');
    } finally {
      setIsAutoFilling(false);
    }
  };

  const progress = totalQuestions > 0 ? (currentStep / totalQuestions) * 100 : 0;

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-2xl">
      {/* Header */}
      <div className="px-8 py-6 border-b bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-t-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">Client Onboarding</h2>
            <p className="text-lg text-purple-100 mt-2">
              {currentStage} • Question {currentStep + 1} of {totalQuestions}
            </p>
          </div>
          {isCompleted && (
            <CheckCircle2 className="w-12 h-12 text-green-300" />
          )}
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4 bg-white/20 rounded-full h-3">
          <div
            className="bg-white rounded-full h-3 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="px-8 py-4 bg-red-50 border-b border-red-200 flex items-center gap-3 text-red-800">
          <AlertCircle className="w-6 h-6" />
          <span className="text-base">{error}</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-5">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-xl px-6 py-4 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white text-lg'
                  : message.content.includes('phase-complete') || 
                    message.content.includes('welcome-back') ||
                    message.content.includes('karen-intro') ||
                    message.content.includes('karen-complete')
                  ? 'p-0 bg-transparent'
                  : 'bg-gray-100 text-gray-900 text-lg'
              }`}
            >
              {message.content.includes('<div') ? (
                <div dangerouslySetInnerHTML={{ __html: message.content }} />
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
              <p
                className={`text-sm mt-2 ${
                  message.role === 'user' ? 'text-purple-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {(isLoading || isStreaming) && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-xl px-6 py-4 flex items-center gap-3">
              <Loader2 className="w-6 h-6 animate-spin text-gray-600" />
              <span className="text-gray-600 text-lg">
                {isStreaming ? 'Karen is typing...' : 'Thinking...'}
              </span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!isCompleted && (
        <div className="px-8 py-6 border-t bg-gray-50 rounded-b-2xl">
          <div className="flex gap-3">
            <button
              onClick={autoFillResponse}
              disabled={isLoading || isAutoFilling || isStreaming || !sessionId}
              className="px-6 py-4 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              title="Auto-fill with AI-generated answer"
            >
              {isAutoFilling ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <Sparkles className="w-6 h-6" />
              )}
            </button>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isStreaming ? "Karen is typing..." : "Type your answer..."}
              disabled={isLoading || isStreaming || !sessionId}
              className="flex-1 px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading || isStreaming || !sessionId}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-lg font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  <Send className="w-6 h-6" />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {isCompleted && (
        <div className="px-8 py-6 border-t bg-green-50 rounded-b-2xl">
          <div className="flex items-center gap-4 text-green-800">
            <CheckCircle2 className="w-8 h-8" />
            <div>
              <p className="font-semibold text-xl">Onboarding Complete!</p>
              <p className="text-base text-green-700">
                All information has been collected successfully.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
