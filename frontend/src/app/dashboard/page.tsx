'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    avgPrice: 0,
    recentChanges: 0,
  });
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const products = await apiClient.getProducts({ limit: 1000 });
      const logsData = await apiClient.getPriceChangeLogs({ limit: 10 });

      setStats({
        totalProducts: products.length,
        avgPrice: products.length > 0 
          ? products.reduce((sum: number, p: any) => sum + p.current_price, 0) / products.length 
          : 0,
        recentChanges: logsData.length,
      });
      setLogs(logsData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Total Products</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {stats.totalProducts}
          </p>
        </div>

        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Average Price</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            ${stats.avgPrice.toFixed(2)}
          </p>
        </div>

        <div className="card">
          <h3 className="text-sm font-medium text-gray-500">Recent Price Changes</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {stats.recentChanges}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a
              href="/dashboard/evaluate"
              className="p-4 border-2 border-indigo-500 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <h3 className="font-semibold text-indigo-900">🤖 AI Price Evaluation</h3>
              <p className="text-sm text-indigo-700 mt-1">
                Upload product image & get AI-powered price
              </p>
            </a>

            <a
              href="/dashboard/stores"
              className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Manage Stores</h3>
              <p className="text-sm text-gray-600 mt-1">
                Create and manage your store locations
              </p>
            </a>

            <a
              href="/dashboard/products"
              className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Manage Products</h3>
              <p className="text-sm text-gray-600 mt-1">
                View and edit your product catalog
              </p>
            </a>

            <a
              href="/dashboard/pricing"
              className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Price Optimization</h3>
              <p className="text-sm text-gray-600 mt-1">
                Get AI-powered pricing recommendations
              </p>
            </a>

            <a
              href="/dashboard/simulation"
              className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Run Simulation</h3>
              <p className="text-sm text-gray-600 mt-1">
                Backtest pricing strategies
              </p>
            </a>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="overflow-hidden">
            {logs.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {logs.map((log) => (
                  <li key={log.id} className="py-3">
                    <div className="flex justify-between">
                      <p className="text-sm font-medium text-gray-900">
                        Product #{log.product_id}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(log.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex justify-between mt-1">
                      <p className="text-sm text-gray-500">
                        ${log.old_price} → <span className="text-green-600 font-medium">${log.new_price}</span>
                      </p>
                      <p className="text-xs text-gray-400 capitalize">
                        {log.reason.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm text-center py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
