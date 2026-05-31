import api from './index'

export const resolveWrong = (bankId, questionId) =>
  api.post(`/wrong/${bankId}/${questionId}/resolve`)
