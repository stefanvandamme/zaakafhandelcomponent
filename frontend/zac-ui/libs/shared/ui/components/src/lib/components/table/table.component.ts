import {animate, state, style, transition, trigger} from "@angular/animations";
import {AfterViewInit, Component, EventEmitter, Input, OnChanges, OnInit, Output, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import {Table, TableSort} from '@gu/models';
import {TableService} from "./table.service";


interface TableButtonClickEvent {
  [key: string]: any
}

interface TableSortEvent {
  value: string,
  order: 'asc' | 'desc'
}

/**
 * <gu-table [table]="tableData"></gu-table>
 *
 * Generic table component, based on mat-table.
 *
 * Requires table: Table input for main tabular data.
 * Takes expandable: boolean as toggle to allow expanding rows (if available).
 * Takes sortable: boolean as toggle to allow sorting.
 * Takes wrap: boolean as toggle to allow wrapping.
 *
 * Emits buttonOutput: TableButtonClickEvent output when a button is clicked.
 * Emits sortOutput: SortEvent output when the table gets sorted.
 * Emits tableOutput: any output when a row is clicked.
 */
@Component({
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({height: '0px', minHeight: '0'})),
      state('expanded', style({height: '*'})),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
  providers: [TableService],
  selector: 'gu-table',
  styleUrls: ['./table.component.scss'],
  templateUrl: './table.component.html',
})
export class TableComponent implements OnInit, AfterViewInit, OnChanges {
  @Input() expandable = false;
  @Input() sortable = false;
  @Input() table: Table;
  @Input() wrap = false;

  @Output() tableOutput = new EventEmitter<any>();
  @Output() buttonOutput = new EventEmitter<any>();
  @Output() sortOutput = new EventEmitter<any>();

  @ViewChild(MatSort) sort: MatSort;

  columns: { name: string, label: string }[];
  uiColumns: { name: string, label: string }[];
  displayedColumns: string[];
  dataSource: MatTableDataSource<any>;
  expandedElement: Object;

  /**
   * Constructor method.
   * @param {TableService} tableService
   */
  constructor(private tableService: TableService) {
    this.table = this.table || {headData: [], bodyData: []};
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

  /**
   * A lifecycle hook that is called after Angular has fully initialized a component's view. Define an ngAfterViewInit()
   * method to handle any additional initialization tasks.
   */
  ngAfterViewInit(): void {
    if (!this.dataSource) {
      return;
    }

    this.dataSource.sort = this.sort;
    this.dataSource.sortingDataAccessor = (data, sortHeadId) => {
      const element = data[sortHeadId];
      return element.value || element.label;
    }
  }

  /**
   * A lifecycle hook that is called when any data-bound property of a directive changes. Define an ngOnChanges() method
   * to handle the changes.
   */
  ngOnChanges(): void {
    this.getContextData();
  }

  //
  // Context.
  //

  /**
   * Sets/updates the required attributes for the table to work.
   */
  getContextData(): void {
    // Table data not ready.
    if (!this.table) {
      return;
    }

    // Set context.
    this.columns = this.tableService.tableDataAsColumns(this.table);
    this.displayedColumns = this.tableService.getDisplayedColumnNames(this.columns, this.expandable);
    this.dataSource = this.tableService.createOrUpdateMatTableDataSource(this.table, this.dataSource);
  }

  //
  // Events.
  //

  /**
   * Gets called when a button is clicked, emits buttonOutput.
   * @param {string} columnName
   * @param {*} value
   */
  onButtonClick(columnName: string, value: any): void {
    if (columnName && value) {
      const output = {
        [columnName]: value
      }
      this.buttonOutput.emit(output as TableButtonClickEvent);
    }
  }

  /**
   * Gets called when a nested button is clicked, emits buttonOutput.
   * @param {Object} event Output of (nested) onButtonClick().
   */
  onNestedButtonClick(event: Object): void {
    this.buttonOutput.emit(event as TableButtonClickEvent);
  }

  /**
   * Gets called when a row is clicked, emits tableOutput.
   * @param {*} value
   */
  onRowClick(value: any): void {
    if (value) {
      this.tableOutput.emit(value as any);
    }
  }

  /**
   * Gets called when a column is sorted.
   * @param {active: string, direction: 'asc' | 'desc'} event
   */
  onSort(event: { active: string, direction: 'asc' | 'desc' }): void {
    const output: TableSort = {
      value: event.active,
      order: event.direction,
    }
    this.sortOutput.emit(output as TableSortEvent);
  }
}
