import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDrawer, MatDrawerContainer } from '@angular/material/sidenav';
import { NzButtonSize } from 'ng-zorro-antd/button';
import { AppService } from './core/api/app/app.service';
import { NavigationEnd, Router } from '@angular/router';
import { ConfigService } from './core/api/config/config.service';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'open-data';
  size: NzButtonSize = 'large';
  dateRange: any = null;
  apiUrl: any;
  activeRoute: string = '';

  constructor(
    private appService: AppService,
    private router: Router,
    private configService: ConfigService
  ) { }

  ngOnInit() {
    this.getDateRange();
  }

  getDateRange() {
    this.appService.getDataDateRange().subscribe(
      (response: any) => {
        this.appService.setselectedDate(new Date(response.max_date));
        this.appService.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
      },
      (error: Error) => {
        console.log(error);
      }
    )
  }

  
}
