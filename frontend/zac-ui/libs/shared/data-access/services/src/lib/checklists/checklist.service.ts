import {Injectable} from '@angular/core';
import {ApplicationHttpClient} from '@gu/services';
import {Observable} from 'rxjs';
import {HttpParams} from '@angular/common/http';
import {Checklist, ChecklistAnswer, ChecklistQuestion, ChecklistType, User, UserGroupDetail} from '@gu/models';


@Injectable({
  providedIn: 'root'
})
export class ChecklistService {
  constructor(private http: ApplicationHttpClient) {
  }

  /**
   * List checklisttype and related questions.
   * @param {string} zaaktypeUrl URL-reference of the ZAAKTYPE related to the checklisttype.
   * @return {Observable<ChecklistType[]>}
   */
  listChecklistTypeAndRelatedQuestions(zaaktypeUrl: string): Observable<ChecklistType[]> {
    const endpoint = encodeURI(`/api/checklists/checklisttypes`);
    const params = new HttpParams().set('zaaktype', zaaktypeUrl);

    return this.http.Get<ChecklistType[]>(endpoint, {
      params: params
    });
  }

  /**
   * Create checklisttype and related questions.
   * @param {ChecklistQuestion[]} checklistQuestions
   * @param {string} zaaktypeUrl URL-reference of the ZAAKTYPE related to the checklisttype.
   * @return {Observable<ChecklistType>}
   */
  createChecklistTypeAndRelatedQuestions(checklistQuestions: ChecklistQuestion[], zaaktypeUrl: string): Observable<ChecklistType> {
    const endpoint = encodeURI(`/api/checklists/checklisttypes`);
    const params = new HttpParams();
    params.set('questions', checklistQuestions as any);
    params.set('zaaktype', zaaktypeUrl);

    return this.http.Post<ChecklistType>(endpoint, params);
  }

  /**
   * Update checklisttype and related questions.
   * @param {string} uuid A UUID string identifying this checklist type.
   * @param {ChecklistQuestion[]} checklistQuestions
   * @param {string} zaaktypeUrl URL-reference of the ZAAKTYPE related to the checklisttype.
   * @return {Observable<ChecklistType>}
   */
  updateChecklistTypeAndRelatedQuestions(uuid: string, checklistQuestions: ChecklistQuestion[], zaaktypeUrl: string): Observable<ChecklistType> {
    const endpoint = encodeURI(`/api/checklists/checklisttypes/${uuid}`);
    const params = new HttpParams();
    params.set('questions', checklistQuestions as any);
    params.set('zaaktype', zaaktypeUrl);

    return this.http.Put<ChecklistType>(endpoint, params);
  }

  /**
   * List checklist and related answers.
   * @param {string} zaakUrl URL-reference of the ZAAK related to the checklist.
   * @return {Observable<Checklist[]>}
   */
  listChecklistAndRelatedAnswers(zaakUrl: string): Observable<Checklist[]> {
    const endpoint = encodeURI(`/api/checklists/checklists`);
    const params = new HttpParams().set('zaak', zaakUrl);

    return this.http.Get<Checklist[]>(endpoint, {
      params: params
    });
  }

  /**
   * Create checklist and related answers.
   * @param {string} checklistTypeUuid
   * @param {ChecklistAnswer[]} checklistAnswers
   * @param {string} zaakUrl
   */
  createChecklistAndRelatedAnswers(checklistTypeUuid: string, checklistAnswers: ChecklistAnswer[], zaakUrl: string, groupAssignee: UserGroupDetail = null, userAssignee: User = null): Observable<Checklist> {
    const endpoint = encodeURI(`/api/checklists/checklists`);
    const params = new HttpParams();
    params.set('checklistType', checklistTypeUuid);
    params.set('zaak', zaakUrl);
    params.set('answers', checklistAnswers as any);
    params.set('groupAssignee', groupAssignee as any);
    params.set('userAssignee', userAssignee as any);

    return this.http.Post<Checklist>(endpoint, params);
  }

  /**
   * Update checklist and related answers.
   * @param {number} id A unique integer value identifying this checklist.
   * @param {string} checklistTypeUuid
   * @param {ChecklistAnswer[]} checklistAnswers
   * @param {string} zaakUrl
   * @param groupAssignee
   * @param userAssignee
   */
  updateChecklistAndRelatedAnswers(id: number, checklistTypeUuid: string, checklistAnswers: ChecklistAnswer[], zaakUrl: string, groupAssignee: UserGroupDetail = null, userAssignee: User = null): Observable<Checklist> {
    const endpoint = encodeURI(`/api/checklists/checklists/${id}`);
    const params = new HttpParams();
    params.set('checklistType', checklistTypeUuid);
    params.set('zaak', zaakUrl);
    params.set('answers', checklistAnswers as any);
    params.set('groupAssignee', groupAssignee as any);
    params.set('userAssignee', userAssignee as any);

    return this.http.Patch<Checklist>(endpoint, params);
  }
}
