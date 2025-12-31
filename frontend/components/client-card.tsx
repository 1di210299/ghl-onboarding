'use client'

import { type Client } from '@/lib/supabase'
import { MapPin, Mail, Phone, Globe, Facebook, Instagram, Linkedin, Twitter } from 'lucide-react'

interface ClientCardProps {
  client: Client
}

export function ClientCard({ client }: ClientCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">Practice Information</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contact Information */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-500 uppercase">
            Contact Details
          </h3>

          {client.address && (
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
              <div className="text-sm">
                <p>{client.address.street}</p>
                <p>
                  {client.address.city}, {client.address.state}{' '}
                  {client.address.zip}
                </p>
              </div>
            </div>
          )}

          {client.email && (
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <a
                href={`mailto:${client.email}`}
                className="text-sm text-blue-600 hover:underline"
              >
                {client.email}
              </a>
            </div>
          )}

          {client.phone && (
            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-gray-400" />
              <a
                href={`tel:${client.phone}`}
                className="text-sm text-blue-600 hover:underline"
              >
                {client.phone}
              </a>
            </div>
          )}

          {client.website && (
            <div className="flex items-center gap-3">
              <Globe className="w-5 h-5 text-gray-400" />
              <a
                href={client.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                {client.website}
              </a>
            </div>
          )}
        </div>

        {/* Branding & Preferences */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-500 uppercase">
            Branding & Preferences
          </h3>

          {client.terminology_preference && (
            <div>
              <p className="text-sm text-gray-600 mb-1">Terminology</p>
              <p className="text-sm font-medium capitalize">
                {client.terminology_preference}
              </p>
            </div>
          )}

          {client.brand_colors && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Brand Colors</p>
              <div className="flex gap-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded border border-gray-200"
                    style={{ backgroundColor: client.brand_colors.primary }}
                  />
                  <span className="text-xs text-gray-600">
                    {client.brand_colors.primary}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded border border-gray-200"
                    style={{ backgroundColor: client.brand_colors.secondary }}
                  />
                  <span className="text-xs text-gray-600">
                    {client.brand_colors.secondary}
                  </span>
                </div>
              </div>
            </div>
          )}

          {client.social_links && (
            <div>
              <p className="text-sm text-gray-600 mb-2">Social Media</p>
              <div className="flex gap-2">
                {client.social_links.facebook && (
                  <a
                    href={client.social_links.facebook}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    <Facebook className="w-4 h-4 text-blue-600" />
                  </a>
                )}
                {client.social_links.instagram && (
                  <a
                    href={client.social_links.instagram}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    <Instagram className="w-4 h-4 text-pink-600" />
                  </a>
                )}
                {client.social_links.linkedin && (
                  <a
                    href={client.social_links.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    <Linkedin className="w-4 h-4 text-blue-700" />
                  </a>
                )}
                {client.social_links.twitter && (
                  <a
                    href={client.social_links.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    <Twitter className="w-4 h-4 text-blue-400" />
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Business Goals */}
      {client.business_goals && client.business_goals.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">
            Business Goals
          </h3>
          <ul className="space-y-2">
            {client.business_goals.map((goal, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600 font-medium">{index + 1}.</span>
                <span className="text-sm">{goal}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
