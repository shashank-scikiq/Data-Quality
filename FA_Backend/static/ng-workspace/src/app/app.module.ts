import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { MaterialModule } from './material/material.module';
import { HttpClientModule } from '@angular/common/http';
import { ZorroModule } from './zorro/zorro.module';
import { FormsModule } from '@angular/forms';


import { registerLocaleData } from '@angular/common';
import en from '@angular/common/locales/en';
registerLocaleData(en);

import { provideNzI18n, en_US } from 'ng-zorro-antd/i18n';
import { NgApexchartsModule } from 'ng-apexcharts';

import { DqReportComponent } from './components/dq-report/dq-report.component';
import { DatePickerComponent } from './components/global/forms/date-picker/date-picker.component';


@NgModule({
  declarations: [
    AppComponent,
    // HeaderComponent,
    // DataDirectoryComponent,
    // LicenseComponent,
    // RightSidenavComponent,
    // PincodeMappingComponent,
    // DomainMappingComponent,
    // DataDirectoryDetailComponent,
    DqReportComponent,
    // LandingPageComponent,
    // CommonLayoutComponent,
    // LayoutComponent,
    // LandingPageChartComponent,
    DatePickerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MaterialModule,
    ZorroModule,
    FormsModule,
    HttpClientModule,
    NgApexchartsModule,
    // LogisticModule,
    // RetailModule,
    // SharedModule
  ],
  providers: [
    provideAnimationsAsync(),
    provideNzI18n(en_US)
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
