
getProject = """query Project($projectId: ID!) {
  project(id: $projectId) {
    documents {
      id
      transcriptionType
      transcriptionStatus
    }
  }
}"""
getAudioFile = """mutation Mutation($documentId: ID!) {
  getPresignedUrlForAudioFile(documentId: $documentId) {
    url
    expiresAtUnixSeconds
  }
}"""
getJSONDocument = """query Query($documentId: ID!) {
  documentJSON(documentId: $documentId)
}"""