import api from './index'

export function getIssues(params) {
  return api.get('/admin/issues', { params })
}

export function getIssueDetail(issueId) {
  return api.get(`/admin/issues/${issueId}`)
}

export function resolveIssue(issueId) {
  return api.patch(`/admin/issues/${issueId}/resolve`)
}

export function reopenIssue(issueId) {
  return api.patch(`/admin/issues/${issueId}/reopen`)
}
