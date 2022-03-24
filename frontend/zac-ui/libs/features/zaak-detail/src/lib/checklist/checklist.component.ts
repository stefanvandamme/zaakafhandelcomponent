import {Component, Input, OnChanges, OnInit} from '@angular/core';
import {FieldConfiguration, SnackbarService} from '@gu/components';
import {
  Checklist,
  ChecklistAnswer,
  ChecklistQuestion,
  ChecklistType,
  QuestionChoice,
  User,
  Zaak
} from '@gu/models';
import {ChecklistService, UserService, ZaakService} from '@gu/services';
import {KetenProcessenService} from '../keten-processen/keten-processen.service';
import {UserGroupResult} from '../../models/user-group-search';
import {UserSearchResult} from '../../models/user-search';


/**
 * <gu-checklist [bronorganisatie]="bronorganisatie" [identificatie]="identificatie"></gu-checklist>
 *
 * Shows checklist.
 *
 * Requires bronorganisatie: string input to identify the organisation.
 * Requires identificatie: string input to identify the case (zaak).
 */
@Component({
  selector: 'gu-checklist',
  templateUrl: './checklist.component.html',
})
export class ChecklistComponent implements OnInit, OnChanges {
  @Input() mainZaakUrl: string;
  @Input() bronorganisatie: string;
  @Input() identificatie: string;
  @Input() zaaktypeOmschrijving: string;

  readonly errorMessage = 'Er is een fout opgetreden bij het laden van checklists.'

  /** @type {boolean} Whether the API is loading. */
  isLoading = false;

  /** @type {ChecklistType[]} The checklist type (array of 1). */
  checklistTypes: ChecklistType[] = [];

  /** @type {Checklist[]} The checklist (array of 1). */
  checklists: Checklist[] = [];

  /** @type {FieldConfiguration[]} The checklist form. */
  checklistForms: FieldConfiguration[][] = null;

  /** @type {User[]} */
  users: UserSearchResult[] = []

  /** @type {Group[]} */
  groups: UserGroupResult[] = []

  /** @type {Zaak} The zaak object. */
  zaak: Zaak = null;

  /**
   * Constructor method.
   * @param {ChecklistService} checklistService
   * @param {KetenProcessenService} ketenProcessenService
   * @param {SnackbarService} snackbarService
   * @param {UserService} userService
   * @param {ZaakService} zaakService
   */
  constructor(
    private checklistService: ChecklistService,
    private ketenProcessenService: KetenProcessenService,
    private snackbarService: SnackbarService,
    private userService: UserService,
    private zaakService: ZaakService,
  ) {
  }

  //
  // Getters / setters.
  //

  //
  // Angular lifecycle.
  //

  /**
   * A lifecycle hook that is called after Angular has initialized all data-bound properties of a directive. Define an
   * ngOnInit() method to handle any additional initialization tasks.
   */
  ngOnInit(): void {
  }

  /**
   * A lifecycle hook that is called when any data-bound property of a directive changes. Define an ngOnChanges() method
   * to handle the changes.
   */
  ngOnChanges(): void {
    this.getContextData();
  };

  //
  // Context.
  //

  /**
   * Fetches the properties to show in the form.
   */
  getContextData(): void {
    this.fetchChecklistData();
    this.fetchUsers();
    this.fetchGroups();
  }

  /**
   * Fetches the user.
   */
  fetchUsers(): void {
    this.ketenProcessenService.getAccounts('').subscribe((userSearch) => {
      this.users = userSearch.results;
      this.checklistForms = this.getChecklistForms();
    });
  }

  /**
   * Fetches the user.
   */
  fetchGroups(): void {
    this.ketenProcessenService.getUserGroups('').subscribe((userGroupList) => {
      this.groups = userGroupList.results;
      this.checklistForms = this.getChecklistForms();
    });
  }

  /**
   * Fetches the ChecklistTypes and Checklists, creates forms.
   */
  fetchChecklistData(): void {
    this.isLoading = true;
    const result = this.zaakService.retrieveCaseDetails(this.bronorganisatie, this.identificatie).subscribe(
      (zaak) => {
        this.zaak = zaak;

        this.checklistService.listChecklistTypeAndRelatedQuestions(zaak.url).subscribe(
          (checklistTypes: ChecklistType[]) => {
            this.checklistTypes = checklistTypes;

            this.checklistService.listChecklistAndRelatedAnswers(zaak.url).subscribe(
              (checklists: Checklist[]) => {
                this.checklists = checklists;

                console.log(this.zaak, this.checklistTypes, this.checklists);
                this.checklistForms = this.getChecklistForms();
                this.isLoading = false;
              },
              this.reportError.bind(this)
            )
          },
          this.reportError.bind(this),
        );
      },
      this.reportError.bind(this)
    );
  }

  /**
   * Returns a FieldConfiguration[] (form) for every ChecklistType.
   * @return {FieldConfiguration[][]}
   */
  getChecklistForms(): FieldConfiguration[][] {
    return this.checklistTypes.map((checklistType: ChecklistType) => this.getChecklistForm(checklistType));
  }

  /**
   * Returns a FieldConfiguration[] (form) for a ChecklistType.
   * @param {ChecklistType} checklistType
   * @return {FieldConfiguration[]}
   */
  getChecklistForm(checklistType: ChecklistType): FieldConfiguration[] {
    const checklist = this.checklists.length ? this.checklists[0] : null;

    const fieldConfigurations = checklistType.questions.map((question: ChecklistQuestion) => {
      const answer = checklist?.answers.find((checklistAnswer) => checklistAnswer.question === question.question);

      return ({
        label: question.question,
        name: question.question,
        value: answer?.answer,
        choices: (question.isMultipleChoice)
          ? question.choices.map((questionChoice: QuestionChoice) => ({
            label: questionChoice.name,
            value: questionChoice.value,
          }))
          : null,
      });
    });

    return [...fieldConfigurations, {
      name: 'uuid',
      type: 'hidden',
      value: checklistType.uuid,
    }, {
      label: 'Toegewezen gebruiker',
      name: 'userAssignee',
      required: false,
      choices: this.users.map((user: UserSearchResult) => ({label: user.username, value: user.username})),
      value: checklist.userAssignee?.username,
    }, {
      label: 'Toegewezen groep',
      name: 'groupAssignee',
      required: false,
      choices: this.groups.map((group: UserGroupResult) => ({label: group.name, value: group.name})),
      value: checklist.groupAssignee?.name,
    }]
  }

  //
  // Events.
  //

  /**
   * Gets called when a checklist form is submitted.
   * @param {Object} data
   */
  submitForm(data): void {
    const {uuid, userAssignee, groupAssignee, ...answerData} = data;
    const answers: ChecklistAnswer[] = Object.entries(answerData).map(([question, answer]) => ({
      question: question,
      answer: answer as string,
      created: new Date().toISOString()
    }));

    if (this.checklists.length) {
      this.checklistService.updateChecklistAndRelatedAnswers(this.checklists[0]['id'],  uuid, answers, this.zaak.url, userAssignee, groupAssignee).subscribe(
        this.fetchChecklistData.bind(this),
        this.reportError.bind(this),
      );
    } else {
      this.checklistService.createChecklistAndRelatedAnswers(uuid, answers, this.zaak.url, userAssignee, groupAssignee).subscribe(
        this.fetchChecklistData.bind(this),
        this.reportError.bind(this),
      );
    }
  }

  //
  // Error handling.
  //

  /**
   * Error callback.
   * @param {*} error
   */
  reportError(error: any): void {
    const message = this.errorMessage;
    this.snackbarService.openSnackBar(message, 'Sluiten', 'warn');
    this.isLoading = false;
    console.error(error);
  }
}
