export interface User {
  id: number;
  email: string;
  role: string;
  created_at: string;
}

export interface Product {
  id: number;
  store_id: number;
  sku: string;
  title: string;
  cost_price: number;
  current_price: number;
  min_price: number;
  max_price: number;
  inventory: number;
  stock_age_days: number;
  metadata: Record<string, any>;
  last_price_change?: string;
  cooldown_seconds: number;
  created_at: string;
  updated_at?: string;
}

export interface PriceRecommendation {
  new_price: number;
  confidence: number;
  reason: string;
  predicted_revenue_change: number;
  stockout_prediction: number;
}

export interface PriceChangeLog {
  id: number;
  product_id: number;
  old_price: number;
  new_price: number;
  reason: string;
  confidence: number;
  created_at: string;
}

export interface SimulationResult {
  simulation_id: number;
  store_id: number;
  predicted_revenue_change: number;
  csv_download_url: string;
}
