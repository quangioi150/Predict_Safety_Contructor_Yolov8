import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Result } from '../interfaces/result.interface';

@Injectable({
  providedIn: 'root'
})
export class ResultServiceService {
  private readonly baseURL = "http://127.0.0.1:5000/"

  constructor(private httpClient: HttpClient) { }

  // public getAllResult(): Observable<any> {
  //   var param = JSON.parse(localStorage.getItem("userInfo")).UserID
  //   return this.httpClient.get<any>(this.baseURL + "get/"+ param )
  // }
  public getAllesult() : void {}
  public deleteResult(id:number): Observable<any> {
    return this.httpClient.delete<any>(this.baseURL + "delete_result_by_id/" +id)
  }
  public addResult(UserID: number, LinkImg:string, Img: any) {
    var param = `results?UserID=${UserID}&LinkImg=${LinkImg}`
    return this.httpClient.post<any>(this.baseURL + param,Img)
  }
  public uploadImage(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.httpClient.post<any>(`${this.baseURL}`, formData);
  }
}
