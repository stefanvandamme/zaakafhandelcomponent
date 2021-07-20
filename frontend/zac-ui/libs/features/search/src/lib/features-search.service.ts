import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApplicationHttpClient } from '@gu/services';
import { ZaaktypeEigenschap } from '../models/zaaktype-eigenschappen';
import { Zaaktype } from '../models/zaaktype';
import { Search } from '../models/search';
import { TableSort } from '@gu/models';
import { tableHeadMapping } from './search-results/constants/table';
import { ReportQuery } from '../models/report';

@Injectable({
  providedIn: 'root'
})
export class FeaturesSearchService {

  constructor(private http: ApplicationHttpClient) { }

  getZaaktypen(): Observable<Zaaktype> {
    const endpoint = encodeURI("/api/core/zaaktypen");
    return this.http.Get<Zaaktype>(endpoint);
  }

  getZaaktypeEigenschappen(catalogus, zaaktype_omschrijving): Observable<ZaaktypeEigenschap[]> {
    const endpoint = encodeURI(`/api/core/eigenschappen?catalogus=${catalogus}&zaaktype_omschrijving=${zaaktype_omschrijving}`);
    return this.http.Get<ZaaktypeEigenschap[]>(endpoint);
  }

  postSearchZaken(formData: Search, sortData?: TableSort): Observable<any> {
    const sortOrder = sortData?.order === 'desc' ? '-' : '';
    const sortValue = sortData ? tableHeadMapping[sortData.value] : '';
    const sortParameter = sortData ? `?ordering=${sortOrder}${sortValue}` : '';
    const endpoint = encodeURI(`/api/search/zaken${sortParameter}`);
    return this.http.Post<any>(endpoint, formData);
  }

  postCreateReport(formData: ReportQuery): Observable<any> {
    const endpoint = encodeURI('/api/search/reports/');
    return this.http.Post<any>(endpoint, formData);
  }
}
