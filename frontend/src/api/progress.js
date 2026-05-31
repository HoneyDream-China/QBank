import api from './index'

export const getProgress = (bankId) => api.get(`/progress/${bankId}`)
export const submitAnswer = (data) => api.post('/progress/answer', data)
export const submitExam = (data) => api.post('/progress/submit-exam', data)
export const getRandomRecords = (bankId) => api.get(`/progress/${bankId}/random-records`)
export const getSeqIndex = (bankId) => api.get(`/progress/${bankId}/seq-index`)
