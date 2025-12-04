'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function StoresPage() {
  const [stores, setStores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newStoreName, setNewStoreName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadStores();
  }, []);

  const loadStores = async () => {
    try {
      const data = await apiClient.getStores();
      setStores(data);
    } catch (error) {
      console.error('Error loading stores:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStore = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Generate a simple random API key
      const apiKey = 'sk_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      await apiClient.createStore({ name: newStoreName, api_key: apiKey });
      setNewStoreName('');
      setIsCreating(false);
      loadStores();
    } catch (error) {
      console.error('Error creating store:', error);
    }
  };

  const handleDeleteStore = async (id: number) => {
    if (!confirm('Are you sure you want to delete this store?')) return;
    try {
      await apiClient.deleteStore(id);
      loadStores();
    } catch (error) {
      console.error('Error deleting store:', error);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading stores...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Stores</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
        >
          Add Store
        </button>
      </div>

      {isCreating && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Create New Store</h2>
          <form onSubmit={handleCreateStore} className="flex gap-4">
            <input
              type="text"
              value={newStoreName}
              onChange={(e) => setNewStoreName(e.target.value)}
              placeholder="Store Name"
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border"
              required
            />
            <button
              type="submit"
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {stores.map((store) => (
          <div key={store.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold text-gray-900">{store.name}</h3>
              <button
                onClick={() => handleDeleteStore(store.id)}
                className="text-red-500 hover:text-red-700"
              >
                Delete
              </button>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">ID:</span> {store.id}</p>
              <p><span className="font-medium">API Key:</span> <code className="bg-gray-100 px-1 rounded">{store.api_key}</code></p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
