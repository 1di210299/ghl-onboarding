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
              ¡Onboarding Completado!
            </h1>
            <p className="text-gray-600 mb-4">
              Gracias por completar el proceso de onboarding.
            </p>
            <p className="text-sm text-gray-500">
              Hemos recibido toda tu información y pronto nos pondremos en contacto contigo.
            </p>
          </div>

          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              <strong>Próximos pasos:</strong>
            </p>
            <ul className="text-sm text-blue-700 mt-2 text-left space-y-1">
              <li>✓ Revisaremos tu información</li>
              <li>✓ Crearemos tu perfil en nuestro sistema</li>
              <li>✓ Te contactaremos en las próximas 24-48 horas</li>
            </ul>
          </div>

          <button
            onClick={() => window.location.href = '/'}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Volver al Inicio
          </button>
        </div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to Client Onboarding
            </h1>
            <p className="text-gray-600">
              Let's get started with your healthcare practice setup
            </p>
          </div>

          <form onSubmit={handleStart} className="space-y-4">
            <div>
              <label
                htmlFor="practiceName"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Practice Name *
              </label>
              <input
                id="practiceName"
                type="text"
                required
                value={formData.practiceName}
                onChange={(e) =>
                  setFormData({ ...formData, practiceName: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Healthy Life Medical"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Email Address *
              </label>
              <input
                id="email"
                type="email"
                required
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="contact@practice.com"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              Start Onboarding
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            This will take approximately 15-20 minutes
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto py-8">
        <div className="h-[calc(100vh-8rem)]">
          <OnboardingChat
            tenantId={formData.tenantId}
            practiceName={formData.practiceName}
            email={formData.email}
            onComplete={handleComplete}
          />
        </div>
      </div>
    </div>
  );
}
