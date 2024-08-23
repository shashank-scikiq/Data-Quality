import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '@openData/env/environment';
import { BehaviorSubject, Subject, of, switchMap, takeUntil } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class AppService {

  private baseUrl: string | null = null;

  currentUrl = new BehaviorSubject<any>('');
  currentUrl$ = this.currentUrl.asObservable();

  metrix = new BehaviorSubject<any>('map_total_orders_metrics');
  selectedMetrix$ = this.metrix.asObservable();

  stateData = new BehaviorSubject<any>(null);
  stateData$ = this.stateData.asObservable();

  isDownloadDataDialogOpen = new BehaviorSubject<boolean>(false);
  isDownloadDataDialogOpen$ = this.isDownloadDataDialogOpen.asObservable();

  selectedDate = new BehaviorSubject<any>(null);

  choosableDateRange = new BehaviorSubject<any>(null);
  public maxDate: BehaviorSubject<any>;
  selectedDate$ = this.selectedDate.asObservable();
  choosableDateRange$ = this.choosableDateRange.asObservable();

  stateAndDistrictData = new BehaviorSubject<any>(null);

  selectedSellerNP = new BehaviorSubject<any>('All');


  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
    this.maxDate = new BehaviorSubject<any>(null);
  }

  setMetrix(value: any) {
    this.metrix.next(value);
  }

  setSelectedSellerNP(value: string) {
    this.selectedSellerNP.next(value);
  }

  setStateAndDistrictData(value: any) {
    this.stateAndDistrictData.next(value);
  }

  getStateAndDistrictData() {
    return this.stateAndDistrictData.getValue();
  }

  getStateDistrictData() {
    return this.http.get(`${this.baseUrl}api/state_district_list/`);
  }

  setStateData(data: any) {
    this.stateData.next(data);
  }

  setCurrentUrl(url: string) {
    this.currentUrl.next(url);
  }

  setIsDownloadDataDialogOpen(value: boolean) {
    this.isDownloadDataDialogOpen.next(value);
  }

  getDataDateRange(uri: string = '') {
    if (uri) {
      return this.http.get(`${this.baseUrl}api/${uri}/get-max-date/`);
    }
    else {
      return this.http.get(`${this.baseUrl}api/get-max-date/`);
    }
  }

  setChoosableDateRange(value: any) {
    this.choosableDateRange.next(value);
  }

  getMaxDate() {
    return this.maxDate;
  }

  setselectedDate(value: any) {
    this.selectedDate.next(value);
  }

  setMaxDate(value: any) {
    this.maxDate.next(value);
  }

  formatDate(date: Date) {
    let d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear();

    if (month.length < 2)
      month = '0' + month;
    if (day.length < 2)
      day = '0' + day;

    return [year, month, day].join('-');
  }
  
  // dq-apis
  private cancelTrend1Previous$ = new Subject<void>();
  getTrend1Data() {
    this.cancelTrend1Previous$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq_report/trend_1/`, {params}).pipe(
      takeUntil(this.cancelTrend1Previous$)
    );
  }

  // private cancelTrend2Previous$ = new Subject<void>();
  // getTrend2Data() {
  //   this.cancelTrend2Previous$.next();
  //   let date_val = this.formatDate(this.selectedDate.value);
  //   const params = {
  //     date_val,
  //     seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
  //   }
  //   return this.http.get(this.baseUrl + `api/dq_report/trend_2/`, {params}).pipe(
  //     takeUntil(this.cancelTrend2Previous$)
  //   );
  // }

  private cancelDetailCompletedTableDataPrevious$ = new Subject<void>();
  getDetailCompletedTableData() {
    this.cancelDetailCompletedTableDataPrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq_report/detail_completed_table_data/`, {params}).pipe(
      takeUntil(this.cancelDetailCompletedTableDataPrevious$)
    );
  }


  private cancelDetailCancelTableDataPrevious$ = new Subject<void>();
  getDetailCancelTableData() {
    this.cancelDetailCancelTableDataPrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq_report/detail_cancel_table_data/`, {params}).pipe(
      takeUntil(this.cancelDetailCancelTableDataPrevious$)
    );
  }

  private cancelHighestMissingPIDPrevious$ = new Subject<void>();
  getCancelHighestMissingData() {
    this.cancelHighestMissingPIDPrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq_report/cancel_highest_missing_pid_data/`, {params}).pipe(
      takeUntil(this.cancelHighestMissingPIDPrevious$)
    );
  }


  private cancelRadialChartrevious$ = new Subject<void>();
  getRadialChartData() {
    this.cancelRadialChartrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq/missing_percentage/`, {params}).pipe(
      takeUntil(this.cancelRadialChartrevious$)
    );
  }

  private cancelDQTopCardPrevious$ = new Subject<void>();
  getDQTopCardData() {
    this.cancelDQTopCardPrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val,
      seller_np: this.selectedSellerNP.value === 'All' ? '' : this.selectedSellerNP.value
    }
    return this.http.get(this.baseUrl + `api/dq_report/top_card/`, {params}).pipe(
      takeUntil(this.cancelDQTopCardPrevious$)
    );
  }

  private cancelSellerNpPrevious$ = new Subject<void>();
  getSellerNpData() {
    this.cancelSellerNpPrevious$.next();
    let date_val = this.formatDate(this.selectedDate.value);
    const params = {
      date_val
    }
    return this.http.get(this.baseUrl + `api/dq_report/sellers_np/`, {params}).pipe(
      takeUntil(this.cancelSellerNpPrevious$)
    );
  }

  getDataSanityTableData() {
    return this.http.get(this.baseUrl + `api/dq_report/data_sanity/last_run_date_data/`);
  }

  getDataVarianceTableData() {
    return this.http.get(this.baseUrl + `api/dq_report/data_sanity/variance_data/`);
  }
}
