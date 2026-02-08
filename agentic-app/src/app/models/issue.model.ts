export interface Issue {
  userID: string;
  userName: string;
  issueDescription: string;
  issueTitle: string;
  threadID: string;
  imageURL?: string;
  audioURL?: string;
  caseId?: string;
}