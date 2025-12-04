'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function SimulationPage() {
  const [stores, setStores] = useState<any[]>([]);
  const [selectedStore, setSelectedStore] = useState<number | null>(null);
  const [days, setDays] = useState(30);
  const [strategy, setStrategy] = useState('revenue_maximize');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStores();
  }, []);

  const loadStores = async () => {
    try {
      const data = await apiClient.getStores();
      setStores(data);
      if (data.length > 0) setSelectedStore(data[0].id);
    } catch (error) {
      console.error('Error loading stores:', error);
    }
  };

  const handleRunSimulation = async () => {
    if (!selectedStore) return;
    setLoading(true);
    try {
      const data = await apiClient.runSimulation(selectedStore, days, strategy);
      setResults(data);
    } catch (error) {
      console.error('Error running simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Strategy Simulation</h1>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Store</label>
            <select
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={selectedStore || ''}
              onChange={(e) => setSelectedStore(Number(e.target.value))}
            >
              {stores.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Duration (Days)</label>
            <input
              type="number"
              min="1"
              max="365"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Strategy</label>
            <select
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
            >
              <option value="revenue_maximize">Maximize Revenue</option>
              <option value="profit_maximize">Maximize Profit</option>
              <option value="market_share">Market Share</option>
            </select>
          </div>
        </div>
        <div className="mt-6">
          <button
            onClick={handleRunSimulation}
            disabled={loading || !selectedStore}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      {results && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
              <p className="mt-2 text-3xl font-semibold text-green-600">
                ${results.total_revenue.toFixed(2)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-sm font-medium text-gray-500">Total Profit</h3>
              <p className="mt-2 text-3xl font-semibold text-blue-600">
                ${results.total_profit.toFixed(2)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-sm font-medium text-gray-500">Units Sold</h3>
              <p className="mt-2 text-3xl font-semibold text-gray-900">
                {results.total_units_sold}
              </p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Daily Breakdown</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Day</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Units</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.daily_breakdown.map((day: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Day {index + 1}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${day.revenue.toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${day.profit.toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{day.units_sold}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
