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
    if (!input.trim() || !sessionId || isLoading) return;

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

      // Add bot response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.bot_message,
          timestamp: new Date(),
        },
      ]);

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
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
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
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Client Onboarding</h2>
            <p className="text-sm text-blue-100 mt-1">
              {currentStage} • Question {currentStep + 1} of {totalQuestions}
            </p>
          </div>
          {isCompleted && (
            <CheckCircle2 className="w-8 h-8 text-green-300" />
          )}
        </div>
        
        {/* Progress Bar */}
        <div className="mt-3 bg-white/20 rounded-full h-2">
          <div
            className="bg-white rounded-full h-2 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="px-6 py-3 bg-red-50 border-b border-red-200 flex items-center gap-2 text-red-800">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              <p
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-gray-600" />
              <span className="text-gray-600 text-sm">Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!isCompleted && (
        <div className="px-6 py-4 border-t bg-gray-50 rounded-b-lg">
          <div className="flex gap-2">
            <button
              onClick={autoFillResponse}
              disabled={isLoading || isAutoFilling || !sessionId}
              className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              title="Auto-fill with AI-generated answer"
            >
              {isAutoFilling ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
            </button>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your answer..."
              disabled={isLoading || !sessionId}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading || !sessionId}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {isCompleted && (
        <div className="px-6 py-4 border-t bg-green-50 rounded-b-lg">
          <div className="flex items-center gap-3 text-green-800">
            <CheckCircle2 className="w-6 h-6" />
            <div>
              <p className="font-semibold">Onboarding Complete!</p>
              <p className="text-sm text-green-700">
                All information has been collected successfully.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
