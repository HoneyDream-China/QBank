import api from './index'

export const getBanks = () => api.get('/banks/')
export const createBank = (data) => api.post('/banks/', data)
export const updateBank = (id, data) => api.put(`/banks/${id}`, data)
export const deleteBank = (id) => api.delete(`/banks/${id}`)
