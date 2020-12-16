import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// Material Icons
import { MatIconModule } from '@angular/material/icon';

// UI Elements
import { ButtonComponent } from './elements/button/button.component';
import { ChipComponent } from './elements/chip/chip.component';
import { LoadingIndicatorComponent } from './elements/loading-indicator/loading-indicator.component';
import { RadioComponent } from './elements/radio/radio.component';
import { TableComponent } from './elements/table/table.component';
import { TooltipComponent } from './elements/tooltip/tooltip.component';

// UI Components
import { FileComponent } from './components/file/file.component';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { SuccessComponent } from './components/success/success.component';

@NgModule({
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatIconModule],
  declarations: [
    ButtonComponent,
    ChipComponent,
    FileComponent,
    FileUploadComponent,
    LoadingIndicatorComponent,
    RadioComponent,
    TableComponent,
    TooltipComponent,
    SuccessComponent,
  ],
  exports: [
    ButtonComponent,
    ChipComponent,
    FileComponent,
    FileUploadComponent,
    LoadingIndicatorComponent,
    RadioComponent,
    TableComponent,
    TooltipComponent,
    SuccessComponent,
  ],
})
export class SharedUiComponentsModule {}
