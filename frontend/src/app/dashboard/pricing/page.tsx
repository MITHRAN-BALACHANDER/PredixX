'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function PricingPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    const data = await apiClient.getProducts({ limit: 100 });
    setProducts(data);
  };

  const handleGetRecommendation = async () => {
    if (!selectedProduct) return;
    setLoading(true);
    try {
      const data = await apiClient.getPriceRecommendation(selectedProduct);
      setRecommendation(data);
    } catch (error) {
      console.error('Error getting recommendation:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Price Optimization</h1>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="max-w-xl">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Product</label>
          <div className="flex gap-4">
            <select
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              onChange={(e) => setSelectedProduct(Number(e.target.value))}
              value={selectedProduct || ''}
            >
              <option value="">Select a product...</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} ({p.sku}) - ${p.current_price}
                </option>
              ))}
            </select>
            <button
              onClick={handleGetRecommendation}
              disabled={!selectedProduct || loading}
              className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>
      </div>

      {recommendation && (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Recommendation</h2>
            <div className="flex items-baseline gap-2 mb-4">
              <span className="text-4xl font-bold text-green-600">${recommendation.recommended_price.toFixed(2)}</span>
              <span className="text-sm text-gray-500">Recommended Price</span>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Confidence Score</span>
                <span className="font-medium">{(recommendation.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Predicted Demand</span>
                <span className="font-medium">{recommendation.predicted_demand.toFixed(1)} units</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Projected Revenue</span>
                <span className="font-medium">${recommendation.projected_revenue.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Analysis Factors</h2>
            <div className="space-y-2">
              {Object.entries(recommendation.factors || {}).map(([key, value]: [string, any]) => (
                <div key={key} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium text-gray-700 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm text-gray-600">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
