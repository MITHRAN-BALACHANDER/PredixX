const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async register(email: string, password: string, role: string = 'merchant') {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, role }),
    });
  }

  // Products endpoints
  async getProducts(params: { limit?: number; skip?: number; store_id?: number; sku?: string } = {}) {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', String(params.limit));
    if (params.skip) queryParams.append('skip', String(params.skip));
    if (params.store_id) queryParams.append('store_id', String(params.store_id));
    if (params.sku) queryParams.append('sku', params.sku);
    
    const query = queryParams.toString();
    return this.request(`/products${query ? `?${query}` : ''}`);
  }

  async createProduct(data: any) {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProduct(id: number) {
    return this.request(`/products/${id}`);
  }

  async updateProduct(id: number, data: any) {
    return this.request(`/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteProduct(id: number) {
    return this.request(`/products/${id}`, {
      method: 'DELETE',
    });
  }

  // Stores endpoints
  async getStores() {
    return this.request('/stores');
  }

  async createStore(data: { name: string; api_key: string }) {
    return this.request('/stores', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getStore(id: number) {
    return this.request(`/stores/${id}`);
  }

  async updateStore(id: number, data: any) {
    return this.request(`/stores/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteStore(id: number) {
    return this.request(`/stores/${id}`, {
      method: 'DELETE',
    });
  }

  // Pricing endpoints
  async getPriceRecommendation(productId: number) {
    return this.request('/price/recommend', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId }),
    });
  }

  async toggleAutoPricing(storeId: number, enabled: boolean) {
    return this.request('/price/auto', {
      method: 'POST',
      body: JSON.stringify({ store_id: storeId, enabled }),
    });
  }

  async runSimulation(storeId: number, days: number, strategy: string) {
    return this.request('/price/simulate', {
      method: 'POST',
      body: JSON.stringify({ store_id: storeId, days, strategy }),
    });
  }

  // Logs endpoints
  async getPriceChangeLogs(params: { limit?: number; skip?: number; product_id?: number } = {}) {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', String(params.limit));
    if (params.skip) queryParams.append('skip', String(params.skip));
    if (params.product_id) queryParams.append('product_id', String(params.product_id));
    
    const query = queryParams.toString();
    return this.request(`/logs/price-changes${query ? `?${query}` : ''}`);
  }

  // ML endpoints
  async predictPrice(
    productName: string,
    description: string,
    quantity: number,
    image?: File
  ) {
    const formData = new FormData();
    formData.append('product_name', productName);
    formData.append('description', description);
    formData.append('quantity', String(quantity));
    if (image) {
      formData.append('image', image);
    }

    const token = this.getToken();
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
      const error = await response.json().catch(() => ({ detail: 'Prediction failed' }));
      throw new Error(error.detail || 'Prediction failed');
    }

    return response.json();
  }

  async predictPriceJson(data: { product_name: string; description: string; quantity: number }) {
    return this.request('/ml/predict-json', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMlStatus() {
    return this.request('/ml/status');
  }
}

export const apiClient = new ApiClient();
