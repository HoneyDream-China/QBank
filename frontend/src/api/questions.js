import api from './index'

export const getQuestions = (bankId, mode = 'seq') =>
  api.get(`/banks/${bankId}/questions`, { params: { mode } })

export const getQuestion = (bankId, questionId) =>
  api.get(`/banks/${bankId}/questions/${questionId}`)

export const createQuestion = (bankId, data) =>
  api.post(`/banks/${bankId}/questions`, data)

export const updateQuestion = (bankId, questionId, data) =>
  api.put(`/banks/${bankId}/questions/${questionId}`, data)

export const deleteQuestion = (bankId, questionId) =>
  api.delete(`/banks/${bankId}/questions/${questionId}`)
