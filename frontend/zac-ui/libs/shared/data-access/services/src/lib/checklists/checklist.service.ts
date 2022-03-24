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
   * @param {string} zaakUrl URL-reference of the ZAAK with ZAAKTYPE related to the checklisttype.
   * @return {Observable<ChecklistType[]>}
   */
  listChecklistTypeAndRelatedQuestions(zaakUrl: string): Observable<ChecklistType[]> {
    const endpoint = encodeURI(`/api/checklists/checklisttypes`);
    const params = new HttpParams().set('zaak', zaakUrl);

    return this.http.Get<ChecklistType[]>(endpoint, {
      params: params
    });
  }

  // /**
  //  * Create checklisttype and related questions.
  //  * @param {ChecklistQuestion[]} checklistQuestions
  //  * @param {string} zaaktypeUrl URL-reference of the ZAAKTYPE related to the checklisttype.
  //  * @return {Observable<ChecklistType>}
  //  */
  // createChecklistTypeAndRelatedQuestions(checklistQuestions: ChecklistQuestion[], zaaktypeUrl: string): Observable<ChecklistType> {
  //   const endpoint = encodeURI(`/api/checklists/checklisttypes`);
  //
  //   return this.http.Post<ChecklistType>(endpoint, {
  //     questions: checklistQuestions,
  //     zaaktype: zaaktypeUrl,
  //   });
  // }

  /**
   * Update checklisttype and related questions.
   * @param {string} uuid A UUID string identifying this checklist type.
   * @param {ChecklistQuestion[]} checklistQuestions
   * @param {string} zaaktypeUrl URL-reference of the ZAAKTYPE related to the checklisttype.
   * @return {Observable<ChecklistType>}
   */
  updateChecklistTypeAndRelatedQuestions(uuid: string, checklistQuestions: ChecklistQuestion[], zaaktypeUrl: string): Observable<ChecklistType> {
    const endpoint = encodeURI(`/api/checklists/checklisttypes/${uuid}`);

    return this.http.Put<ChecklistType>(endpoint, {
      questions: checklistQuestions,
      zaaktype: zaaktypeUrl,
    });
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
   * @param {string} userAssignee
   * @param {string} groupAssignee
   */
  createChecklistAndRelatedAnswers(checklistTypeUuid: string, checklistAnswers: ChecklistAnswer[], zaakUrl: string, userAssignee: string = null, groupAssignee: string = null): Observable<Checklist> {
    const endpoint = encodeURI(`/api/checklists/checklists`);

    const params = {
      checklistType: checklistTypeUuid,
      zaak: zaakUrl,
      answers: checklistAnswers,
    }

    if (userAssignee) {
      params['userAssignee'] = userAssignee;
    } else {
      params['groupAssignee'] = groupAssignee;
    }

    return this.http.Post<Checklist>(endpoint, params);
  }

  /**
   * Update checklist and related answers.
   * @param {number} id A unique integer value identifying this checklist.
   * @param {string} checklistTypeUuid
   * @param {ChecklistAnswer[]} checklistAnswers
   * @param {string} zaakUrl
   * @param {string} userAssignee
   * @param {string} groupAssignee
   */
  updateChecklistAndRelatedAnswers(id: number, checklistTypeUuid: string, checklistAnswers: ChecklistAnswer[], zaakUrl: string, userAssignee: string = null, groupAssignee: string = null): Observable<Checklist> {
    const endpoint = encodeURI(`/api/checklists/checklists/${id}`);

    const params = {
      checklistType: checklistTypeUuid,
      zaak: zaakUrl,
      answers: checklistAnswers,
    }

    if (userAssignee) {
      params['userAssignee'] = userAssignee;
    } else {
      params['groupAssignee'] = groupAssignee;
    }

    return this.http.Put<Checklist>(endpoint, params);
  }
}
