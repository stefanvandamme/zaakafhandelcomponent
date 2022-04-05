import {UserGroupDetail} from '../accounts/user-group';
import {User} from '../accounts/user';

export interface ChecklistAnswer {
  question: string,
  answer: string,
  created: string,
}

export interface Checklist {
  answers: ChecklistAnswer[],
  groupAssignee?: UserGroupDetail,
  userAssignee?: User,
  url?: string,
  created?: string,
}
