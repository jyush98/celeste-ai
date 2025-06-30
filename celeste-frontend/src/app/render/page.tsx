'use client'

import { useState } from 'react'

export default function RenderPage() {
    const [prompt, setPrompt] = useState('')
    const [imageUrl, setImageUrl] = useState('')
    const [loading, setLoading] = useState(false)

    const handleGenerate = async () => {
        setLoading(true)
        setImageUrl('')

        const res = await fetch('http://localhost:8002/generate-jewelry-image', {
            method: 'POST',
        })

        const data = await res.json()
        const fullUrl = `http://localhost:8002/${data.image_url}`
        setImageUrl(fullUrl)
        setLoading(false)
    }

    return (
        <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center px-4 py-12">

            <h1 className="text-3xl font semibold mb-6"> Celeste AI Jewelry Render</h1>

            <textarea
                className="w-full max-w-xl h-32 p-4 rounded-lg bg-gray-900 border border-gray-700 text-white"
                placeholder="Describe your custom jewelry idea..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
            />

            <button
                onClick={handleGenerate}
                disabled={loading}
                className="mt-4 px-6 py-3 bg-white text-black font-bold rounded-lg hover:bg-gray-300 disabled:opacity-50"
            >
                {loading ? 'Generating...' : 'Generate Image'}
            </button>

            {imageUrl && (
                <img
                    src={imageUrl}
                    alt={imageUrl}
                    className="mt-8 max-w-md rounded-lg border border-white"
                />
            )}
        </div>
    )
}