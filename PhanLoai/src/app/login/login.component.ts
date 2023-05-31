import { ChangeDetectorRef, Component, EventEmitter, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ResultServiceService } from '../service/result-service.service';
import { UserServiceService } from '../service/user-service.service';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  @Output() newItemEvent = new EventEmitter<string>();
  formLogin: FormGroup;
  formRegister: FormGroup;
  Date: Date

  public passwordTextTypeLogin!: boolean;
  public passwordTextTypeRegister!: boolean;
  isLogin = false;
  returnUrl!: string;
  siteKey: string = "6Lerft8gAAAAAGMh4wmSQR7oPqOV2wvLJhE1KOc8"
  constructor(
    private fb: FormBuilder,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private messageService: MessageService,
    private userService: UserServiceService,
    private resultService: ResultServiceService
  ) {
    this.formLogin = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
    });
    this.formRegister = this.fb.group({
      name: ['', Validators.required],
      username: ['', Validators.required],
      dob: ['', Validators.required],
      password: ['', Validators.required],
      address: ['', Validators.required],
    });
  }
  userId: string
  ngOnInit(): void {
  }
  togglePasswordTextTypeLogin(event) {
    this.passwordTextTypeLogin = !this.passwordTextTypeLogin;
    this.cdr.detectChanges();
  }

  togglePasswordTextTypeRegister(event) {
    this.passwordTextTypeRegister = !this.passwordTextTypeRegister;
    this.cdr.detectChanges();
  }

  login(userId: string) {
    this.newItemEvent.emit(userId);
    let user = this.formLogin.controls["username"].value;
    let password = this.formLogin.controls["password"].value;
    console.log(user, password)
    this.userService.login(user,password).subscribe({
      next: (data: any)=> {
        console.log(data)
        if(typeof(data.User.UserID) == "number") {
          localStorage.setItem("userInfo", JSON.stringify(data));
          this.router.navigateByUrl("classify")

        }
        else {
          this.messageService.add({severity:'error', summary: 'Error', detail: 'Tài khoản hoặc mật khẩu không đúng'});
        }
      },error: error => {
        this.messageService.add({severity:'error', summary: 'Error', detail: 'Tài khoản hoặc mật khẩu không đúng'});
      }
    })
  }

  register() {
    let UserID = 5
    let name = this.formRegister.controls["name"].value;
    let username = this.formRegister.controls["username"].value;
    let dob = this.formRegister.controls["dob"].value;
    let address = this.formRegister.controls["address"].value;
    let password = this.formRegister.controls["password"].value;
    this.userService.register(name,username,address,dob,password).subscribe({
      next: (data:any )=> {
        console.log(data)
        if(data.HoTen != null) {
          this.formRegister.reset();
          this.messageService.add({severity:'success', summary:'Success', detail: 'Đăng ký tài khoản thành công'})
        }
      },error: error => {
        this.messageService.add({severity:'error', summary: 'Error', detail: 'Lỗi trong quá trình tạo tài khoản'});
      }
    })
  }

}
