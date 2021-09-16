import {Component, Input, OnInit} from '@angular/core';
import {FieldConfiguration, ModalService, SnackbarService} from '@gu/components';
import {ObjectType, RowData, Table, ZaakObject, ZaakObjectGroup} from '@gu/models';
import {ZaakObjectService, ZaakService} from '@gu/services';

/**
 * <gu-gerelateerde-objecten [bronorganisatie]="bronorganisatie" [identificatie]="identificatie"></gu-gerelateerde-objecten>
 *
 * Shows related objects for a case (zaak).
 *
 * Requires bronorganisatie: string input to identify the organisation.
 * Requires identificatie: string input to identify the case (zaak).
 */
@Component({
  selector: 'gu-gerelateerde-objecten',
  templateUrl: './gerelateerde-objecten.component.html',
  styleUrls: ['./gerelateerde-objecten.component.scss']
})
export class GerelateerdeObjectenComponent implements OnInit {
  @Input() bronorganisatie: string;
  @Input() identificatie: string;

  /** @type {string} Possible error message. */
  readonly errorMessage = 'Er is een fout opgetreden bij het zoeken naar gerelateerde objecten.'

  /** @type {string} Modal id. */
  readonly modalObjectSearchId = 'related-objects-object-search-modal';

  /** @type {string} Modal id. */
  readonly modalFormId = 'related-objects-form-modal';

  /** @type {ZaakObject} The selected zaak object (to relate to resolved zaak). */
  activeZaakObject: ZaakObject = null;

  /** @type {boolean} Whether this component is loading. */
  isLoading: boolean;

  /** @type {ZaakObjectGroup[]} The list of groups of objects (Related objects are grouped on objecttype) */
  relatedObjects: ZaakObjectGroup[];

  /**
   * Constructor method.
   * @param {ModalService} modalService
   * @param {SnackbarService} snackbarService
   * @param {ZaakService} zaakService
   */
  constructor(private modalService: ModalService, private snackbarService: SnackbarService, private zaakService: ZaakService, private zaakObjectService: ZaakObjectService) {
  }

  //
  // Getters / setters.
  //

  get form(): FieldConfiguration[] {
    return [
      {
        label: 'Gerelateerd object toevoegen:',
        name: 'object',
        readonly: true,
        value: (this.activeZaakObject)
          ? this.zaakObjectService.stringifyZaakObject(this.activeZaakObject)
          : null,
      },
      {
        label: 'Beschrijving',
        name: 'objectTypeDescription',
        pattern: "[a-zA-Z_]{1,100}",
        placeholder: 'Beschrijving van het type object (maximaal 100 tekens).',
        value: '',
      }
    ];
  }

  /**
   * Returns the tables to render.
   * @returns {{title: string, table: Table}[]}
   */
  get tables(): { title: string; table: Table }[] {
    return this.relatedObjects.map((group: ZaakObjectGroup) => {
      /* Use the latest version of the ObjectType to make the table headers */
      const latestZaakObjectGroup = group.items[0];
      const latestZaakObjectGroupType = latestZaakObjectGroup.type as ObjectType;
      const objectProperties: [] = latestZaakObjectGroupType.versions[latestZaakObjectGroupType.versions?.length - 1]
        .jsonSchema.required;

      const tableHead: string[] = [
        ...objectProperties.filter((property): boolean => property !== 'objectid'),
        'acties',
      ]

      const tableBody: RowData[] = group.items.map((relatedObject: ZaakObject) => {
        const cellData = tableHead.reduce((acc, val: string) => {
          acc[val] = String(relatedObject.record.data[val] || '');
          return acc;
        }, {});

        cellData['acties'] = {
          label: 'Verwijderen',
          name: 'delete',
          type: 'button',
          value: relatedObject,
        }

        return {
          cellData: cellData
        };
      });

      const table = new Table(tableHead, tableBody);
      return {title: group.label, table: table};
    });
  }

  //
  // Angular lifecycle.
  //

  /**
   * A lifecycle hook that is called after Angular has initialized all data-bound properties of a directive. Define an
   * ngOnInit() method to handle any additional initialization tasks.
   */
  ngOnInit(): void {
    this.getContextData();
  }

  //
  // Context.
  //

  /**
   * Fetches the objects related to a zaak
   */
  getContextData(): void {
    this.isLoading = true;

    this.zaakService.listRelatedObjects(this.bronorganisatie, this.identificatie).subscribe(
      (data) => this.relatedObjects = data,
      this.reportError.bind(this),
      () => this.isLoading = false
    );
  }

  //
  // Events.
  //

  /**
   * Gets called when the add related object button is clicked.
   * @param {Event} event
   */
  addClick(event: Event): void {
    this.modalService.open(this.modalObjectSearchId);
  }

  /**
   * Gets called when the form is submitted.
   * @param {Object} data
   */
  formSubmit(data): void {
    this.zaakService.retrieveCaseDetails(this.bronorganisatie, this.identificatie).subscribe(
      (zaak) => this.zaakObjectService
        .createZaakObjectRelation(zaak, this.activeZaakObject, String(data.objectTypeDescription).toLowerCase())
        .subscribe(
          () => {
            this.modalService.close(this.modalFormId);
            this.getContextData.bind(this);
          },
          this.reportError.bind(this)
        ),
      this.reportError.bind(this),
    );
  }

  /**
   * Gets called when a zaak object is selected.
   * @param {ZaakObject} zaakObject
   */
  selectZaakObject(zaakObject: ZaakObject): void {
    this.activeZaakObject = zaakObject;
    this.modalService.close(this.modalObjectSearchId);
    this.modalService.open(this.modalFormId);
  }

  /**
   * Gets called when a delete button in the table is pressed.
   * @param {Object} data
   */
  tableButtonClick(data: { 'acties': ZaakObject }): void {
    this.isLoading = true;

    this.zaakObjectService.deleteZaakObjectRelation(data.acties.zaakobjectUrl).subscribe(
      this.getContextData.bind(this),
      this.reportError.bind(this),
      () => this.isLoading = false
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
    this.snackbarService.openSnackBar(this.errorMessage, 'Sluiten', 'warn');
    console.error(error);
  }

}
