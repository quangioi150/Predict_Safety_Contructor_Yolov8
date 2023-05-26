import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserServiceService {

  private readonly baseURL = "http://localhost:5000"

  constructor(private httpClient: HttpClient, private router: Router) { }

  public getUserByID(): Observable<any> {
    return this.httpClient.get<any>(this.baseURL)
  }
  isLogin= new BehaviorSubject<boolean>(false)
  public login(TenDN: string, MatKhau: string) {
    var body =null

    var param = `/login?TenDN=${TenDN}&MatKhau=${MatKhau}`
      return this.httpClient.post<any>(this.baseURL+param, body)
  }

  public register(HoTen: string, TenDN: string, DiaChi: string, NgaySinh: string, MatKhau: string) {
    var param =  `/user?HoTen=${HoTen}&TenDN=${TenDN}&DiaChi=${DiaChi}&NgaySinh=${NgaySinh}&MatKhau=${MatKhau}`
    var body = null
    return this.httpClient.post<any>(this.baseURL +param, body)
  }

  public update(UserID: number, HoTen: string, TenDN: string, DiaChi: string, NgaySinh: string, MatKhau: string) {
    var param = `/update_user/${UserID}?HoTen=${HoTen}&TenDN=${TenDN}&DiaChi=${DiaChi}&NgaySinh=${NgaySinh}&MatKhau=${MatKhau}`
    var body = null;
    return this.httpClient.put<any>(this.baseURL + param, body)

  }
}
