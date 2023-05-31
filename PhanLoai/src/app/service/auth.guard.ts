import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { UserServiceService } from './user-service.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard  {
  constructor(private router: Router, private userService: UserServiceService) {}
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): boolean {
      let userInfo = JSON.parse(localStorage.getItem("userInfo")).UserID;
      if(userInfo !== 0)
      {
        return true;

      }else{
        this.router.navigate(["/login"])
        return false;
      }
  }
  
}
