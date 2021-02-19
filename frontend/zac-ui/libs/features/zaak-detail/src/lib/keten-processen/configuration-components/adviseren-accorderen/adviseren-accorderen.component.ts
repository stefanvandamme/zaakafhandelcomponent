import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { DatePipe } from '@angular/common';
import { TaskContextData } from '../../../../models/task-context';
import { ApplicationHttpClient } from '@gu/services';
import { Result } from '../../../../models/user-search';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { KetenProcessenService } from '../../keten-processen.service';
import { atleastOneValidator } from '@gu/utils';

@Component({
  selector: 'gu-config-adviseren-accorderen',
  templateUrl: './adviseren-accorderen.component.html',
  styleUrls: ['../configuration-components.scss']
})
export class AdviserenAccorderenComponent implements OnChanges {
  @Input() taskContextData: TaskContextData;

  readonly assignedUsersTitle = {
    advice: 'Adviseur(s)',
    approval: 'Accordeur(s)'
  }
  reviewType: 'advice' | 'approval';

  steps = 1;
  minDate = new Date();
  items: Result[] = [];

  // Form
  assignUsersForm: FormGroup;

  constructor(
    private http: ApplicationHttpClient,
    private fb: FormBuilder,
    private ketenProcessenService: KetenProcessenService,
    private datePipe: DatePipe
  ) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes.taskContextData.previousValue !== this.taskContextData ) {
      this.reviewType = this.taskContextData.context.reviewType;
      this.assignUsersForm = this.fb.group({
        documents: this.addDocumentCheckboxes(),
        assignedUsers: this.fb.array([this.addAssignUsersStep()]),
        toelichting: this.fb.control("", Validators.maxLength(4000))
      })
    }
  }

  addStep() {
    this.steps++
    this.assignedUsers.push(this.addAssignUsersStep());
  }

  deleteStep() {
    this.steps--
    this.assignedUsers.removeAt(this.assignedUsers.length - 1);
  }

  onSearch(searchInput) {
    this.ketenProcessenService.getAccounts(searchInput).subscribe(res => {
      this.items = res.results;
    })
  }

  submitForm() {
    const selectedDocuments = this.documents.value
      .map((checked, i) => checked ? this.taskContextData.context.documents[i].url : null)
      .filter(v => v !== null);
    const assignedUsers = this.assignedUsers.controls
      .map( (step, i) => {
        const deadline = this.datePipe.transform(this.assignedUsersDeadline(i).value, "yyyy-MM-dd");
        const users = this.assignedUsersUsers(i).value;
        return {
          deadline: deadline,
          users: users
        }
      })
    const toelichting = this.toelichting.value;
    const formData = {
      form: this.taskContextData.form,
      assignedUsers: assignedUsers,
      selectedDocuments: selectedDocuments,
      toelichting: toelichting
    };
    this.putForm(formData);
  }

  putForm(formData) {
    this.ketenProcessenService.putTaskData(this.taskContextData.task.id, formData).subscribe(() => {
    })
  }

  addDocumentCheckboxes() {
    const arr = this.taskContextData.context.documents.map(() => {
      return this.fb.control(false);
    });
    return this.fb.array(arr, atleastOneValidator());
  }

  addAssignUsersStep() {
    return this.fb.group({
      deadline: [undefined, Validators.required],
      users: [[], Validators.minLength(1)]
    })
  }

  get documents(): FormArray {
    return this.assignUsersForm.get('documents') as FormArray;
  };

  get assignedUsers(): FormArray {
    return this.assignUsersForm.get('assignedUsers') as FormArray;
  };

  get toelichting(): FormControl {
    return this.assignUsersForm.get('toelichting') as FormControl;
  };

  assignedUsersUsers(index: number): FormControl {
    return this.assignedUsers.at(index).get('users') as FormControl;
  }

  assignedUsersDeadline(index: number): FormControl {
    return this.assignedUsers.at(index).get('deadline') as FormControl;
  }
}
