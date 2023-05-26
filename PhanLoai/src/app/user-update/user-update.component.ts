import { ChangeDetectorRef, Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { DynamicDialogConfig, DynamicDialogRef } from 'primeng/dynamicdialog';
import { User } from '../interfaces/user.interface';
import { UserServiceService } from '../service/user-service.service';

@Component({
  selector: 'app-user-update',
  templateUrl: './user-update.component.html',
  styleUrls: ['./user-update.component.css']
})
export class UserUpdateComponent {
  formGroup: FormGroup;
  create: boolean = true
  // userList: User[]
  constructor(
    private ref: DynamicDialogRef,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private config: DynamicDialogConfig,
    private userService: UserServiceService,
    private messageService: MessageService,
  ) { }
  public userInfor = JSON.parse(localStorage.getItem("userInfo")).User
  public userID = this.userInfor.UserID
    Date: Date;
    user: User
    userLogin: User
    isLogin: boolean = true
  ngOnInit(): void {
    
    this.formGroup = this.fb.group({
      name: [`${this.userInfor.HoTen}`, Validators.required],
      username: [`${this.userInfor.TenDN}`, Validators.required],
      dob: [`${this.userInfor.NgaySinh}`, Validators.required],
      address: [`${this.userInfor.DiaChi}`, Validators.required],
      password: [`${this.userInfor.MatKhau}`, Validators.required],

    });


  }
  getUserById(){
    
  }

  userUpdate(userID: number) {
    userID = this.userID
    let name = this.formGroup.controls["name"].value
    let username = this.formGroup.controls["username"].value
    let dob = this.formGroup.controls["dob"].value
    let address = this.formGroup.controls["address"].value
    let password = this.formGroup.controls["password"].value

    this.userService.update(userID,name,username,dob,address,password).subscribe({
      next: (data: any)=> {
        console.log(data)
        // JSON.parse(localStorage.getItem("userInfo")).userId
        if(data !=null) {
          this.messageService.add({severity:'success', summary:'Success', detail: 'Sửa thông tin thành công'})
          // this.resultService.getAllResult()
          this.userService.login(data.TenDN,data.MatKhau).subscribe({
            next: (data: any)=> {
              console.log(data)
              // JSON.parse(localStorage.getItem("userInfo")).userId
              if(typeof(data.User.UserID) == "number") {
                localStorage.setItem("userInfo", JSON.stringify(data));
                this.router.navigateByUrl("classify")

      
                // this.resultService.getAllResult()
                // window.location.reload();
              }
            },error: error => {
              this.messageService.add({severity:'error', summary: 'Error', detail: 'Tài khoản hoặc mật khẩu không đúng'});
            }
          })
          this.cdr.detectChanges()
          this.ref.close()
          window.location.reload()
        }
      },error: error => {
        this.messageService.add({severity:'error', summary: 'Error', detail: 'Lỗi trong quá trình sửa đổi'});
      }
    })
  }
  Close() {
    this.ref.close()
  }
}
