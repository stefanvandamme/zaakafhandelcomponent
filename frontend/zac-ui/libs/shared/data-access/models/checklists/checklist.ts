import {UserGroupDetail} from '../accounts/user-group';
import {User} from '../accounts/user';

export interface ChecklistAnswer {
  question: string,
  answer: string,
  created: string,
}

export interface Checklist {
  url: string,
  created: string,
  checklistType: string,
  zaak: string,
  answers: ChecklistAnswer[],
  groupAssignee?: UserGroupDetail,
  userAssignee?: User,
}
