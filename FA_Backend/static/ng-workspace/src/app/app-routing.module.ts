import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { DqReportComponent } from './components/dq-report/dq-report.component';

const routes: Routes = [
  {
    path: '',
    component: DqReportComponent
  },
  {
    path: '**',
    redirectTo: ''
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
