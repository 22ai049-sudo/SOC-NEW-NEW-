import { createContext, useContext, useEffect, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => { if (localStorage.getItem('token')) api.get('/api/auth/me').then(setUser).catch(() => localStorage.removeItem('token')); }, []);

  const login = async (username, password) => {
    const token = await api.post('/api/auth/login', { username, password });
    localStorage.setItem('token', token.access_token);
    const me = await api.get('/api/auth/me');
    setUser(me);
  };

  return <AuthContext.Provider value={{ user, login, logout: () => { localStorage.removeItem('token'); setUser(null); } }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
