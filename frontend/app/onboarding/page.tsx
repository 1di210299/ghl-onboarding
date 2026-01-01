'use client';

import OnboardingChat from '@/components/onboarding-chat';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function OnboardingPage() {
  const router = useRouter();
  const [showForm, setShowForm] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);
  const [formData, setFormData] = useState({
    tenantId: '00000000-0000-0000-0000-000000000001',
    practiceName: '',
    email: '',
  });

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.practiceName && formData.email) {
      setShowForm(false);
    }
  };

  const handleComplete = (clientId: string, collectedData: any) => {
    console.log('Onboarding completed!', { clientId, collectedData });
    
    // Show completion message instead of redirecting to dashboard
    setIsCompleted(true);
  };

  // Show completion page
  if (isCompleted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-12 h-12 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Onboarding Complete!
            </h1>
            <p className="text-gray-600 mb-4">
              Thank you for completing the onboarding process.
            </p>
            <p className="text-sm text-gray-500">
              We have received all your information and will contact you soon.
            </p>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>Next steps:</strong>
            </p>
            <ul className="text-sm text-blue-700 mt-2 text-left space-y-1">
              <li>✓ We will review your information</li>
              <li>✓ We will create your profile in our system</li>
              <li>✓ We will contact you within 24-48 hours</li>
            </ul>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-2xl w-full border border-purple-100">
          {/* Karen's Welcome Header */}
          <div className="text-center mb-10">
            <div className="inline-block mb-6">
              <div className="w-32 h-32 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg animate-pulse">
                <span className="text-7xl">✨</span>
              </div>
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
              Hi! I'm Karen 👋
            </h1>
            <p className="text-gray-700 text-2xl font-medium mb-3">
              Your AI Assistant from Staffless Practice
            </p>
            <p className="text-gray-600 text-lg leading-relaxed">
              I'm so excited to help you set up your practice! Let's get to know each other - this will be fun! 🎉
            </p>
          </div>

          <form onSubmit={handleStart} className="space-y-6">
            <div>
              <label
                htmlFor="practiceName"
                className="block text-lg font-semibold text-gray-700 mb-3"
              >
                What's your practice name? 🏥
              </label>
              <input
                id="practiceName"
                type="text"
                required
                value={formData.practiceName}
                onChange={(e) =>
                  setFormData({ ...formData, practiceName: e.target.value })
                }
                className="w-full px-5 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="e.g., Healthy Life Medical"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-lg font-semibold text-gray-700 mb-3"
              >
                What's your email address? 📧
              </label>
              <input
                id="email"
                type="email"
                required
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-5 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                placeholder="contact@practice.com"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-5 rounded-xl font-bold text-xl hover:from-purple-700 hover:to-pink-700 transform hover:scale-[1.02] transition-all shadow-lg hover:shadow-xl"
            >
              Let's Get Started! 🚀
            </button>
          </form>

          <div className="mt-8 p-5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100">
            <p className="text-center text-base text-gray-700">
              <span className="font-semibold text-lg">⏱️ Takes about 15-20 minutes</span>
              <br />
              <span className="text-sm text-gray-600 mt-2 block">
                Don't worry - you can skip any question you're not comfortable with! 💜
              </span>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto h-[calc(100vh-3rem)]">
        <OnboardingChat
          tenantId={formData.tenantId}
          practiceName={formData.practiceName}
          email={formData.email}
          onComplete={handleComplete}
        />
      </div>
    </div>
  );
}
