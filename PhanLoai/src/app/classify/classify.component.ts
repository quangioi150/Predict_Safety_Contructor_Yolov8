import { Binary } from '@angular/compiler';
import { ChangeDetectorRef, Component, ElementRef, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { DialogService } from 'primeng/dynamicdialog';
import { Result } from '../interfaces/result.interface';
import { User } from '../interfaces/user.interface';
import { ResultServiceService } from '../service/result-service.service';
import { ToastMessageService } from '../service/toast-message.service';
import { UserServiceService } from '../service/user-service.service';
import { UserUpdateComponent } from '../user-update/user-update.component';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-classify',
  templateUrl: './classify.component.html',
  styleUrls: ['./classify.component.css'],
  providers: [DialogService]
})

export class ClassifyComponent {
  constructor (private router: Router,
    private messageService: MessageService,
    private toastMessageService: ToastMessageService,
    private resultService: ResultServiceService,
    public dialogService: DialogService,
    public fb: FormBuilder,
    private cdr: ChangeDetectorRef,
    private userService: UserServiceService,
    private http: HttpClient,
    private backendService: ResultServiceService) {}
  imageUrl: string;
  dangerousObjects: string[];

  selectedFile: File | null = null;
  // imageUrl: string | null = null;
  errorMessage: string | null = null;


  // onFileSelected(event: any) {
  //   this.selectedFile = event.target.files[0];
  //   this.errorMessage = null;
  //   this.imageUrl = null;
  // }

  // onUpload() {
  //   if (this.selectedFile) {
  //     this.backendService.uploadImage(this.selectedFile)
  //       .subscribe(
  //         (response) => {
  //           this.imageUrl = response.imageUrl;
  //           console.log(this.imageUrl)
  //           this.errorMessage = this.imageUrl;

  //         },
  //         (error) => {
  //           this.errorMessage = 'Error uploading image.';
  //         }
  //       );
  //   } else {
  //     this.errorMessage = 'Please select an image file.';
  //   }
  // }


  
  @ViewChild('videoElement', { static: true }) videoElement: ElementRef;

  stream: MediaStream;

  startCamera() {
    this.imageURL =''
    this.videoUrl = ''
    document.querySelector('.regular').classList.remove('none') 
    
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          this.stream = stream;
          const video = this.videoElement.nativeElement;
          video.srcObject = stream;
          video.play();
        })
        .catch(error => {
          console.error('Error accessing camera:', error);
        });
    } else {
      console.error('getUserMedia is not supported');
    }
  }

  stopCamera() {
    if (this.stream) {
      const video = this.videoElement.nativeElement;
      const stream = video.srcObject as MediaStream;

      // Stop the video stream
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());

      // Clear the srcObject property
      video.srcObject = null;
    }
  }
  
  public userList: Result[] = [];
  public list: User[]=[];
  // selectedFile: File;
  videoUrl: string;
  uploadForm: FormGroup;
  imageURL: string = '';
  // public userInfor = JSON.parse(localStorage.getItem("userInfo")).User
  ngOnInit(): void {
    this.getAllResult()
    this.uploadForm = this.fb.group({
      avatar: [null],
    })
  }

   
  showPreview(event) {
    const file: File = event.target.files[0];
    const fileType = file.type
    
    const reader = new FileReader();

    reader.onload = (e: any) => {
      if(fileType.startsWith('image/') || // Check MIME type for image files
    ['jpg', 'jpeg', 'png', 'gif'].includes(file.name.split('.').pop())) {
      this.imageURL = e.target.result
      document.querySelector('.regular').classList.add('none') 
    }
    else {
      this.videoUrl = e.target.result;
      this.imageURL = ''
      document.querySelector('.regular').classList.add('none') 
    }
    };

    reader.readAsDataURL(file);
    console.log(this.videoUrl)
    // const file = (event.target as HTMLInputElement).files[0];
    // this.uploadForm.patchValue({
    //   avatar: file
    // });
    // this.uploadForm.get('avatar').updateValueAndValidity()
    // const reader = new FileReader();
    // reader.onload = () => {
    //   this.imageURL = reader.result as string;
    // }
    // reader.readAsDataURL(file)
  }

  getAllResult(){
    // this.resultService.getAllResult().subscribe((data: any) => {
    //   this.userList = [];
    //   console.log(data)
    //   this.userList = data
    //   this.cdr.detectChanges()
    // });
    
  }
  logout() {
    this.router.navigateByUrl("login")
  }

  deleteResult1(ResultID:number) {
    this.toastMessageService.showConfirmDeleteSwal("Kết quả",'này').then(result => {
      if (result.isConfirmed) {
        this.resultService.deleteResult(ResultID).subscribe({next: res => {
          console.log(res)
            this.getAllResult();
        }})
        this.messageService.add({severity:'success', summary: 'Thành công', detail: 'Xóa thành công kết quả'});
      }

    })
  }
  userEdit(id: number) {
    this.dialogService.open(UserUpdateComponent, {
      header: "Chỉnh sửa thông tin người dùng",
      width: "40%",
      data: {
        type: 'edit',
        id: id
      }
    });
  }
  

  classify() {
    // let userid = this.userInfor.UserID
    let linkImg = "http.com"
    let img = this.uploadForm.controls["avatar"].value
    let formData = new FormData
    formData.append("file",img)
    console.log(img)
    
    // this.resultService.addResult(userid, linkImg, formData).subscribe({
    //   next: (data:any )=> {
    //     console.log(data)
    //     this.getAllResult()
    //     if(data.UserID != null) {
    //       this.messageService.add({severity:'success', summary:'Success', detail: 'Phân loại thành công'})
    //     }
    //   },error: error => {
    //     this.messageService.add({severity:'error', summary: 'Error', detail: 'Lỗi trong quá trình phân loại'});
    //   }
    // })

  }
  
}
