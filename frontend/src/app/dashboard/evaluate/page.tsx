'use client';

import { useState, useRef } from 'react';
import { apiClient } from '@/lib/api';

interface PredictionResult {
  predicted_price: number;
  text_price: number | null;
  image_price: number | null;
  image_quality: number | null;
  fusion_method: string;
  confidence: number;
  product_name: string;
  description: string | null;
  quantity: number;
}

export default function EvaluatePage() {
  const [productName, setProductName] = useState('');
  const [description, setDescription] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName.trim()) {
      setError('Product name is required');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.predictPrice(
        productName,
        description,
        quantity,
        image || undefined
      );
      
      if (response.success) {
        setResult(response.prediction);
      } else {
        setError('Prediction failed. Please try again.');
      }
    } catch (err: any) {
      console.error('Prediction error:', err);
      setError(err.response?.data?.detail || 'Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProduct = async () => {
    if (!result) return;
    
    // Redirect to products page with pre-filled data
    const params = new URLSearchParams({
      title: productName,
      description: description,
      predicted_price: result.predicted_price.toString(),
      quantity: quantity.toString()
    });
    window.location.href = `/dashboard/products?${params.toString()}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Price Evaluation</h1>
          <p className="text-gray-600 mt-1">
            Upload product details and image to get AI-powered price predictions
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Product Details</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g., Wireless Bluetooth Headphones"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                rows={4}
                placeholder="Enter product description, features, specifications..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Include details like brand, size, weight, material, features for better predictions
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity / Pack Size
              </label>
              <input
                type="number"
                min="1"
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Image
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-indigo-400 transition-colors">
                {imagePreview ? (
                  <div className="text-center">
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="mx-auto h-32 w-32 object-cover rounded-lg mb-2"
                    />
                    <button
                      type="button"
                      onClick={handleRemoveImage}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Remove image
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      stroke="currentColor"
                      fill="none"
                      viewBox="0 0 48 48"
                    >
                      <path
                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <div className="flex text-sm text-gray-600 mt-2">
                      <label className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500">
                        <span>Upload a file</span>
                        <input
                          ref={fileInputRef}
                          type="file"
                          className="sr-only"
                          accept="image/*"
                          onChange={handleImageChange}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PNG, JPG up to 10MB</p>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !productName.trim()}
              className="w-full bg-indigo-600 text-white px-4 py-3 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </span>
              ) : (
                'Get Price Prediction'
              )}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {result ? (
            <>
              {/* Main Prediction */}
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-6 rounded-lg shadow-lg text-white">
                <h2 className="text-lg font-semibold mb-2 opacity-90">Predicted Price</h2>
                <div className="flex items-baseline">
                  <span className="text-5xl font-bold">${result.predicted_price.toFixed(2)}</span>
                  <span className="ml-2 text-lg opacity-75">USD</span>
                </div>
                <div className="mt-4 flex items-center">
                  <div className="flex-1 bg-white/20 rounded-full h-2">
                    <div 
                      className="bg-white rounded-full h-2 transition-all duration-500"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className="ml-3 text-sm">{(result.confidence * 100).toFixed(0)}% confidence</span>
                </div>
              </div>

              {/* Breakdown */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Price Breakdown</h3>
                <div className="space-y-3">
                  {result.text_price !== null && (
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <div>
                        <p className="font-medium text-blue-900">Text Analysis</p>
                        <p className="text-sm text-blue-600">Based on product name & description</p>
                      </div>
                      <span className="text-xl font-semibold text-blue-900">
                        ${result.text_price.toFixed(2)}
                      </span>
                    </div>
                  )}
                  
                  {result.image_price !== null && (
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-medium text-green-900">Image Analysis</p>
                        <p className="text-sm text-green-600">
                          Quality score: {result.image_quality?.toFixed(1) || 'N/A'}
                        </p>
                      </div>
                      <span className="text-xl font-semibold text-green-900">
                        ${result.image_price.toFixed(2)}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Fusion Method</p>
                      <p className="text-sm text-gray-600">{result.fusion_method}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Next Steps</h3>
                <div className="space-y-3">
                  <button
                    onClick={handleSaveProduct}
                    className="w-full bg-green-600 text-white px-4 py-3 rounded-md hover:bg-green-700 transition-colors font-medium"
                  >
                    Save as New Product
                  </button>
                  <button
                    onClick={() => {
                      setResult(null);
                      setProductName('');
                      setDescription('');
                      setQuantity(1);
                      handleRemoveImage();
                    }}
                    className="w-full border border-gray-300 text-gray-700 px-4 py-3 rounded-md hover:bg-gray-50 transition-colors font-medium"
                  >
                    Evaluate Another Product
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
              <div className="py-12">
                <svg
                  className="mx-auto h-16 w-16 text-gray-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">No prediction yet</h3>
                <p className="mt-2 text-gray-500">
                  Enter product details and click "Get Price Prediction" to see AI-powered pricing suggestions
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
