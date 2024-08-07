


import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
// import * as _moment from 'moment';
// import { default as _rollupMoment, Moment } from 'moment';
// const moment = _rollupMoment || _moment;

@Component({
  selector: 'app-month-range-picker',
  templateUrl: './month-range-picker.component.html',
  styleUrl: './month-range-picker.component.scss'
})
export class MonthRangePickerComponent implements OnInit, OnChanges {
  @Input() dateRange: any = [];
  @Output() selectedDateRange = new EventEmitter<any>();
  availableDateRange: any = [];

  date: any = null;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.date = this.dateRange;
    this.appService.choosableDateRange$.subscribe((val: any) => {
      this.availableDateRange = val;
    });
  }

  checkClear() {
    if(!this.date?.length) {
      return;
    }
    return !(this.date[0].toString()==this.availableDateRange[0].toString() && this.date[1].toString() == this.availableDateRange[1].toString())
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.date = changes['dateRange'].currentValue;
  }

  onChange(result: Date[]): void {
    if (result.length == 0 || result == null || result == undefined) {
      result = this.availableDateRange;
    }
    this.selectedDateRange.emit(result);
  }
  disabledDate = (current: Date): boolean => {
    if (!this.availableDateRange || !current) return false;
  
    const currentMonth = current.getMonth();
    const currentYear = current.getFullYear();
  
    const startMonth = this.availableDateRange[0].getMonth();
    const startYear = this.availableDateRange[0].getFullYear();
    const endMonth = this.availableDateRange[1].getMonth();
    const endYear = this.availableDateRange[1].getFullYear();
  
    // If the current year is before the start year or after the end year, disable the date
    if (currentYear < startYear || currentYear > endYear) {
      return true;
    }
  
    // If the current year is the start year, ensure the month is not before the start month
    if (currentYear === startYear && currentMonth < startMonth) {
      return true;
    }
  
    // If the current year is the end year, ensure the month is not after the end month
    if (currentYear === endYear && currentMonth > endMonth) {
      return true;
    }
  
    // If none of the above conditions are met, enable the date
    return false;
  }
}
  

