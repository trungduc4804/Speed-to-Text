// Fetch wrapper to include JWT and handle basic errors (stub).

const Api = {
  token: null,
  setToken(t) {
    this.token = t;
  },
  async request(path, options = {}) {
    const headers = options.headers || {};
    if (this.token) headers.Authorization = `Bearer ${this.token}`;
    return fetch(path, { ...options, headers });
  },
};

