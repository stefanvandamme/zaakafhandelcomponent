import {Component, Input, OnChanges, OnInit} from '@angular/core';
import {FieldConfiguration, SnackbarService} from '@gu/components';
import {Checklist, ChecklistAnswer, ChecklistQuestion, ChecklistType, QuestionChoice, User, Zaak} from '@gu/models';
import {ChecklistService, UserService, ZaakService} from '@gu/services';


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

  /** @type {FieldConfiguration[]} The checklist form. */
  checklistForms: FieldConfiguration[][] = null;

  /** @type {User} */
  user: User

  /** @type {Zaak} The zaak object. */
  zaak: Zaak = null;

  /**
   * Constructor method.
   * @param {ChecklistService} checklistService
   * @param {SnackbarService} snackbarService
   * @param {UserService} userService
   * @param {ZaakService} zaakService
   */
  constructor(
    private checklistService: ChecklistService,
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
    this.fetchUser();
    this.fetchChecklistData();
  }

  /**
   * Fetches the user.
   */
  fetchUser(): void {
    this.userService.getCurrentUser().subscribe(
      (user: [User, boolean]) => this.user = user[0],
      this.reportError.bind(this)
    )
  }

  /**
   * Fetches the ChecklistTypes and Checklists, creates forms.
   */
  fetchChecklistData(): void {
    this.isLoading = true;
    const result = this.zaakService.retrieveCaseDetails(this.bronorganisatie, this.identificatie).subscribe(
      (zaak) => {
        this.zaak = zaak;

        this.checklistService.listChecklistTypeAndRelatedQuestions(zaak.zaaktype.url).subscribe(
          (checklistTypes: ChecklistType[]) => {
            this.checklistForms = this.getChecklistForms(checklistTypes);

            this.checklistService.listChecklistAndRelatedAnswers(zaak.url).subscribe(
              (checklists: Checklist[]) => {
                console.log('checklists', checklists);
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
   * @param {ChecklistType[]} checklistTypes
   * @return {FieldConfiguration[][]}
   */
  getChecklistForms(checklistTypes: ChecklistType[]): FieldConfiguration[][] {
    return checklistTypes.map((checklistType: ChecklistType) => this.getChecklistForm(checklistType));
  }

  /**
   * Returns a FieldConfiguration[] (form) for a ChecklistType.
   * @param {ChecklistType} checklistType
   * @return {FieldConfiguration[]}
   */
  getChecklistForm(checklistType: ChecklistType): FieldConfiguration[] {
    const fieldConfigurations = checklistType.questions.map((question: ChecklistQuestion) => ({
      label: question.question,
      name: question.question,
      choices: (question.isMultipleChoice)
        ? question.choices.map((questionChoice: QuestionChoice) => ({
          label: questionChoice.name,
          value: questionChoice.value,
        }))
        : null,
    }))
    return [...fieldConfigurations, {
      name: 'uuid',
      type: 'hidden',
      value: checklistType.uuid,
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
    const {uuid, ...answerData} = data;
    const answers: ChecklistAnswer[] = Object.entries(answerData).map(([question, answer]) => ({
      question: question,
      answer: answer as string,
      created: new Date().toISOString()
    }));

    this.checklistService.createChecklistAndRelatedAnswers(uuid, answers, this.zaak.url, this.user.username).subscribe(
      this.fetchChecklistData.bind(this),
      this.reportError.bind(this),
    );
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
