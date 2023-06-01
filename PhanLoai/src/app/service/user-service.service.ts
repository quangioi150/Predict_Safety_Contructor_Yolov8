import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserServiceService {

  private readonly baseURL = "http://127.0.0.1:5000/"

  constructor(private httpClient: HttpClient, private router: Router) { }

  public getUserByID(): Observable<any> {
    return this.httpClient.get<any>(this.baseURL)
  }
  isLogin= new BehaviorSubject<boolean>(false)
  public login(TenDN: string, MatKhau: string) {
    const body = new FormData();
    body.append('user', TenDN);
    body.append('password', MatKhau);
    // var body = {
    //   user: TenDN,
    //   password: MatKhau
    // }

      return this.httpClient.post<any>(this.baseURL+'login', body)
  }

  public register( HoTen: string, TenDN: string, DiaChi: string, NgaySinh: string, MatKhau: string) {
    const body = new FormData();
    body.append('HoTen', HoTen);
    body.append('TenDN', TenDN);
    body.append('DiaChi', DiaChi);
    body.append('NgaySinh', NgaySinh);
    body.append('MatKhau', MatKhau);
    return this.httpClient.post<any>(this.baseURL + 'user', body)
  }

  public update(UserID: number, HoTen: string, TenDN: string, DiaChi: string, NgaySinh: string, MatKhau: string) {
    var param = `/update_user/${UserID}?HoTen=${HoTen}&TenDN=${TenDN}&DiaChi=${DiaChi}&NgaySinh=${NgaySinh}&MatKhau=${MatKhau}`
    var body = null;
    return this.httpClient.put<any>(this.baseURL + param, body)

  }
}
