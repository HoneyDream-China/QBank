import api from './index'

export const adminLogin = (data) => api.post('/auth/admin-login', data)

export const getStats = () => api.get('/admin/stats')

export const getAdminBanks = () => api.get('/admin/banks')

export const adminUpdateBank = (id, name, description) => {
  const fd = new FormData()
  fd.append('name', name)
  fd.append('description', description)
  return api.put(`/admin/banks/${id}`, fd)
}

export const adminDeleteBank = (id) => api.delete(`/admin/banks/${id}`)

export const getAdminQuestions = (bankId) => api.get(`/admin/banks/${bankId}/questions`)

export const adminCreateQuestion = (bankId, data) => api.post(`/admin/banks/${bankId}/questions`, data)

export const adminUpdateQuestion = (bankId, questionId, data) =>
  api.put(`/admin/banks/${bankId}/questions/${questionId}`, data)

export const adminDeleteQuestion = (bankId, questionId) =>
  api.delete(`/admin/banks/${bankId}/questions/${questionId}`)

export const getUsers = () => api.get('/admin/users')

export const uploadPdf = (file, targetBankId, bankName) => {
  const fd = new FormData()
  fd.append('file', file)
  if (targetBankId) fd.append('target_bank_id', targetBankId)
  if (bankName) fd.append('bank_name', bankName)
  return api.post('/admin/upload-pdf', fd)
}

export const importQuestions = (targetBankId, questions) => {
  const fd = new FormData()
  fd.append('target_bank_id', targetBankId)
  fd.append('questions_json', JSON.stringify(questions))
  return api.post('/admin/import-questions', fd)
}

export const createBankWithQuestions = (bankName, bankDescription, questions) => {
  const fd = new FormData()
  fd.append('bank_name', bankName)
  fd.append('bank_description', bankDescription)
  fd.append('questions_json', JSON.stringify(questions))
  return api.post('/admin/create-bank-with-questions', fd)
}
