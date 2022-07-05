import {Component, EventEmitter, Input, OnChanges, OnInit, Output} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from '@angular/forms';
import {UserSearchResult, Zaak, Permission, UserPermission, ZaakPermission} from '@gu/models';
import {AccountsService, ZaakService} from '@gu/services';
import {ModalService, SnackbarService} from '@gu/components';
import {DatePipe} from '@angular/common';

@Component({
  selector: 'gu-toegang-verlenen',
  templateUrl: './toegang-verlenen.component.html',
  styleUrls: ['./toegang-verlenen.component.scss']
})
export class ToegangVerlenenComponent implements OnInit, OnChanges {
  @Input() zaak: Zaak;
  @Output() reload: EventEmitter<any> = new EventEmitter<any>();

  users: UserSearchResult[] = [];
  requesterUser: UserSearchResult;
  permissions: Permission[];
  selectedPermissions: string[];

  grantAccessForm: FormGroup;
  isSubmitting: boolean;
  submitHasError: boolean;
  submitErrorMessage: string;

  submitResult: any;
  submitSuccess: boolean;
  errorMessage: string;

  /**
   * Constructor method.
   * @param {AccountsService} accountsService
   * @param datePipe
   * @param {FormBuilder} fb
   * @param {ModalService} modalService
   * @param {SnackbarService} snackbarService
   * @param {ZaakService} zaakService
   */
  constructor(
    private accountsService: AccountsService,
    private datePipe: DatePipe,
    private fb: FormBuilder,
    private modalService: ModalService,
    private snackbarService: SnackbarService,
    private zaakService: ZaakService,
  ) {
  }

  //
  // Getters / setters.
  //

  get permissionsControl(): FormControl {
    return this.grantAccessForm.get('permissions') as FormControl;
  };

  get requesterControl(): FormControl {
    return this.grantAccessForm.get('requester') as FormControl;
  };

  get endDateControl(): FormControl {
    return this.grantAccessForm.get('endDate') as FormControl;
  };

  //
  // Angular lifecycle.
  //

  ngOnInit(): void {
    this.grantAccessForm = this.fb.group({
      requester: this.fb.control("", Validators.required),
      endDate: this.fb.control("")
    })
    this.getContextData();
  }

  ngOnChanges() {
    this.submitSuccess = false;
  }

  /**
   * Fetch user permissions.
   */
  getContextData() {
    this.accountsService.getPermissions()
      .subscribe(res => {
        this.permissions = res;
        this.selectedPermissions = this.permissions.map(p => p.name)
      }, error => console.error(error))
  }

  /**
   * Update selected permissions.
   * @param event
   */
  updateSelectedPermissions(event) {
    this.selectedPermissions = event.map(p => p.name);
  }

  /**
   * Search users.
   * @param searchInput
   */
  onSearch(searchInput) {
    this.accountsService.getAccounts(searchInput).subscribe(res => {
        this.users = res.results;
      }, error => this.reportError(error)
    );
  }

  /**
   * Gets called when a user is selected.
   * @param user
   */
  onUserChange(user: any) {
    this.zaakService.listCaseUsers(this.zaak.bronorganisatie, this.zaak.identificatie).subscribe(
      (userPermissions: UserPermission[]) => {
        const permission = userPermissions.find((userPermission: UserPermission) => userPermission.username === user.username)

        if (!permission) {
          return
        }

        console.log(permission)
        this.selectedPermissions = permission.permissions.map((zaakPermission: ZaakPermission) => zaakPermission.permission)
        console.log(this.selectedPermissions)
      }
    )
  }

  /**
   * Submit access.
   */
  submitForm() {
    this.isSubmitting = true;
    this.users.forEach(user => {
      if (user.username === this.requesterControl.value) {
        this.requesterUser = user;
      }
    })
    const endDate = this.endDateControl.value ?
      this.datePipe.transform(this.endDateControl.value, "yyyy-MM-dd") :
      undefined;
    const formData = [{
      requester: this.requesterControl.value,
      permissions: this.selectedPermissions,
      endDate: endDate,
      zaak: this.zaak.url
    }];
    this.accountsService.postAccessForCase(formData).subscribe(res => {
      this.submitResult = {
        username: res.requester,
        name: this.requesterUser
      }
      this.submitSuccess = true;
      this.grantAccessForm.reset();
      this.submitHasError = false;
      this.isSubmitting = false;
      this.reload.emit();
    }, error => {
      this.submitErrorMessage =
        error?.error?.detail ? error.error.detail
          : error?.error[0] ? error.error[0].nonFieldErrors[0]
          : 'Er is een fout opgetreden';
      this.reportError(error);
      this.modalService.close('add-person-modal');
    })
  }

  //
  // Error handling.
  //

  /**
   * Error callback.
   * @param {*} error
   */
  reportError(error: any): void {
    this.submitHasError = true;
    this.snackbarService.openSnackBar(this.submitErrorMessage, 'Sluiten', 'warn');
    console.error(error);
    this.isSubmitting = false;
  }
}
