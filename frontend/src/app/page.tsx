'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { 
  Sparkles, 
  Upload, 
  DollarSign, 
  TrendingUp, 
  Package, 
  FileText,
  Loader2,
  CheckCircle,
  AlertCircle,
  Image as ImageIcon,
  X,
  LogOut,
  User
} from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface PredictionResult {
  predicted_price: number;
  text_price: number | null;
  image_price: number | null;
  confidence: number;
  fusion_method: string;
  image_quality: number | null;
}

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user, token, logout } = useAuth();
  
  const [productName, setProductName] = useState('');
  const [description, setDescription] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

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

  const removeImage = () => {
    setImage(null);
    setImagePreview(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('product_name', productName);
      formData.append('description', description);
      formData.append('quantity', String(quantity));
      if (image) {
        formData.append('image', image);
      }

      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/ml/predict`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Prediction failed' }));
        throw new Error(err.detail || 'Prediction failed');
      }

      const data = await response.json();
      setResult(data.prediction);
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setProductName('');
    setDescription('');
    setQuantity(1);
    setImage(null);
    setImagePreview(null);
    setResult(null);
    setError(null);
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Loading state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
      </div>
    );
  }

  // Not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f]">
      {/* Header */}
      <header className="border-b border-[#2a2a2a] bg-[#0f0f0f]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">PredixX</h1>
                <p className="text-xs text-gray-500">AI Price Prediction</p>
              </div>
            </div>

            {/* User Info */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-400">
                <User className="w-4 h-4" />
                <span className="text-sm">{user?.sub || 'User'}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-[#252525] rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-2 gap-8">
          
          {/* Left: Input Form */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Predict Product Price</h2>
              <p className="text-gray-500">Enter product details to get an AI-powered price prediction</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Product Name */}
              <div>
                <label className="label flex items-center gap-2">
                  <Package className="w-4 h-4" />
                  Product Name *
                </label>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  placeholder="e.g., Apple iPhone 15 Pro Max 256GB"
                  className="input"
                />
              </div>

              {/* Description */}
              <div>
                <label className="label flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Product details, specifications, features..."
                  rows={4}
                  className="textarea"
                />
              </div>

              {/* Quantity */}
              <div>
                <label className="label flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Quantity
                </label>
                <input
                  type="number"
                  min={1}
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  className="input w-32"
                />
              </div>

              {/* Image Upload */}
              <div>
                <label className="label flex items-center gap-2">
                  <ImageIcon className="w-4 h-4" />
                  Product Image (Optional)
                </label>
                
                {imagePreview ? (
                  <div className="relative inline-block">
                    <img 
                      src={imagePreview} 
                      alt="Preview" 
                      className="w-32 h-32 object-cover rounded-xl border border-[#3a3a3a]"
                    />
                    <button
                      type="button"
                      onClick={removeImage}
                      className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                    >
                      <X className="w-4 h-4 text-white" />
                    </button>
                  </div>
                ) : (
                  <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-[#3a3a3a] rounded-xl cursor-pointer hover:border-emerald-500/50 transition-colors bg-[#1a1a1a]">
                    <div className="text-center">
                      <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                      <span className="text-sm text-gray-500">Click to upload</span>
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                    />
                  </label>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary flex items-center gap-2 flex-1"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Predicting...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Predict Price
                    </>
                  )}
                </button>
                {(result || error) && (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="btn btn-secondary"
                  >
                    Reset
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Right: Result */}
          <div className="lg:mt-12">
            {result ? (
              <div className="card animate-fadeIn">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Prediction Complete</h3>
                    <p className="text-sm text-gray-500">Based on ML analysis</p>
                  </div>
                </div>

                {/* Main Price */}
                <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 rounded-2xl p-6 mb-6 border border-emerald-500/20">
                  <p className="text-sm text-gray-400 mb-1">Predicted Price</p>
                  <div className="flex items-baseline gap-2">
                    <DollarSign className="w-8 h-8 text-emerald-400" />
                    <span className="text-5xl font-bold text-white">
                      {result.predicted_price.toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    <div className="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                      {(result.confidence * 100).toFixed(0)}% Confidence
                    </div>
                  </div>
                </div>

                {/* Details */}
                <div className="space-y-3">
                  {result.text_price && (
                    <div className="flex items-center justify-between py-3 border-b border-[#2a2a2a]">
                      <span className="text-gray-400 text-sm flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Text Model Price
                      </span>
                      <span className="text-white font-medium">${result.text_price.toFixed(2)}</span>
                    </div>
                  )}
                  {result.image_price && (
                    <div className="flex items-center justify-between py-3 border-b border-[#2a2a2a]">
                      <span className="text-gray-400 text-sm flex items-center gap-2">
                        <ImageIcon className="w-4 h-4" />
                        Image Model Price
                      </span>
                      <span className="text-white font-medium">${result.image_price.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between py-3">
                    <span className="text-gray-400 text-sm">Fusion Method</span>
                    <span className="text-gray-300 text-sm font-mono">{result.fusion_method}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card border-dashed">
                <div className="text-center py-12">
                  <div className="w-16 h-16 rounded-2xl bg-[#252525] flex items-center justify-center mx-auto mb-4">
                    <DollarSign className="w-8 h-8 text-gray-600" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-400 mb-2">No Prediction Yet</h3>
                  <p className="text-sm text-gray-600 max-w-xs mx-auto">
                    Enter product details on the left and click "Predict Price" to get started
                  </p>
                </div>
              </div>
            )}

            {/* Info Cards */}
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="card py-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-500/20 flex items-center justify-center">
                    <FileText className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Text Model</p>
                    <p className="text-sm font-medium text-white">MPNet + TF-IDF</p>
                  </div>
                </div>
              </div>
              <div className="card py-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <ImageIcon className="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Image Model</p>
                    <p className="text-sm font-medium text-white">CLIP ViT-B/32</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
