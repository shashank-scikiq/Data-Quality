import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-date-picker',
  templateUrl: './date-picker.component.html',
  styleUrl: './date-picker.component.scss'
})
export class DatePickerComponent implements OnInit {

  @Input() selectedDate: any = [];
  @Output() selectedDateRange = new EventEmitter<any>();
  availableDateRange: any = [];

  date: any = null;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.date = this.selectedDate;
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

  // ngOnChanges(changes: SimpleChanges): void {
  //   console.log(changes)
  //   this.date = changes['dateRange'].currentValue;
  // }

  onChange(result: Date): void {
    console.log(result, "in on change");
    if (result == null || result == undefined) {
      result = this.availableDateRange[1];
    }
    this.selectedDateRange.emit(result);
  }

  disabledDate = (current: Date): boolean => {
    if (!this.availableDateRange)
      return false;
    return current && (current < this.availableDateRange[0] || current > this.availableDateRange[1]);
  }
}
