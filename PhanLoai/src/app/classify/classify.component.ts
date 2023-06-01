import { Binary } from '@angular/compiler';
import { ChangeDetectorRef, Component, ElementRef, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { Message, MessageService } from 'primeng/api';
import { DialogService } from 'primeng/dynamicdialog';
import { Result } from '../interfaces/result.interface';
import { User } from '../interfaces/user.interface';
import { ResultServiceService } from '../service/result-service.service';
import { ToastMessageService } from '../service/toast-message.service';
import { UserServiceService } from '../service/user-service.service';
import { UserUpdateComponent } from '../user-update/user-update.component';
import { HttpClient } from '@angular/common/http';
import { interval } from 'rxjs';
@Component({
  selector: 'app-classify',
  templateUrl: './classify.component.html',
  styleUrls: ['./classify.component.css'],
  providers: [MessageService, DialogService]
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
  intervalId: any;
  intervalId2: any;
  selectedFile: File | null = null;
  // imageUrl: string | null = null;
  errorMessage: string | null = null;


  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.errorMessage = null;
    this.imageUrl = null;
  }

  onUpload() {
    if (this.selectedFile) {
      this.backendService.uploadImage(this.selectedFile)
        .subscribe(
          (response) => {
            this.imageUrl = response.imageUrl;
            console.log(this.imageUrl)
            this.errorMessage = this.imageUrl;

          },
          (error) => {
            this.errorMessage = 'Error uploading image.';
          }
        );
    } else {
      this.errorMessage = 'Please select an image file.';
    }
  }


  
  @ViewChild('videoElement', { static: true }) videoElement: ElementRef;

  stream: MediaStream;
  link = ''

  startCamera() {
    this.countClick++;
    this.imageURL = ''
    this.videoUrl =''
    if(this.countClick%2!=0) {
      this.camStatus = 'Dừng camera'
      this.isClicked = !this.isClicked
      this.link = 'http://127.0.0.1:5000/video_feed_camera'
      this.intervalId = setInterval(() => this.updateResult(), 2000);
      this.intervalId2 = setInterval(() => this.getResultByUserID(), 2000);
    }
    else {
      this.camStatus = 'Camera'
      this.isClicked = !this.isClicked
      this.link = 'http://127.0.0.1:5000/camera_stop'
      clearInterval(this.intervalId);
      clearInterval(this.intervalId2);
      this.title =''
    }
    
  }
  camStatus: any = 'Camera'
  countClick: any = 0
  countClick2: any = 0
  isClicked = false
  stopCamera() {
    if (this.stream) {
      const video = this.videoElement.nativeElement;
      const stream = video.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      video.srcObject = null;
    }
  }

  stop() {
    this.link = 'http://127.0.0.1:5000/camera_stop'
    clearInterval(this.intervalId);
    this.title =''

  }
  makeGetRequest() {
    const url = 'http://127.0.0.1:5000/api/hello';
    this.http.get(url, { withCredentials: true }).subscribe(response => {
      alert(response['message'])
    });
  }
  
  
  public userList: Result[] = [];
  public list: User[]=[];
  videoUrl: string;
  uploadForm: FormGroup;
  imageURL: string = '';
  public userInfor = JSON.parse(localStorage.getItem("userInfo")).User
  ngOnInit(): void {
    this.getAllResult()
    this.uploadForm = this.fb.group({
      avatar: [null],
    })
    this.getResultByUserID()
    
  }
  resultsByID: any
  getResultByUserID() {
    this.http.get(`http://127.0.0.1:5000/get/${this.userInfor.UserID}`).subscribe(response => {
      this.resultsByID = response
      console.log(this.resultsByID)
      this.cdr.detectChanges();
    })

  }
  title: any =''
  result: any
  messages: Message[]
  updateResult(): void {
    this.http.get('http://127.0.0.1:5000/result',{ withCredentials: true })
      .subscribe(response => {
       
          console.log(response['danger'])
          if (response['danger'] === '') {
            this.result = response['danger'];
            this.title = 'SAFETY';
            this.messages = [
              { severity: 'success', summary: 'SAFETY', detail: 'Everything good' },
          ];
          } else {
            this.result = response['danger'];
            this.title = 'DANGEROUS';
            this.messages = [
              { severity: 'error', summary: 'DANGEROUS', detail: response['danger'] },
          ];
          }
        
      });
  }
   
  showPreview(event) {
    const file: File = event.target.files[0];
    const fileType = file.type
    
    const reader = new FileReader();

    reader.onload = (e: any) => {
      if(fileType.startsWith('image/') || 
    ['jpg', 'jpeg', 'png', 'gif'].includes(file.name.split('.').pop())) {
      this.videoUrl = ''
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
    console.log(this.imageURL)
    this.selectedFile = file
    console.log( this.selectedFile)
  }

  getAllResult(){
    
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
  
  nhanDienStatus: string = 'Nhận diện' 
  classify() {
    console.log( this.selectedFile)

    if (this.selectedFile) {
      if (this.selectedFile.type.includes('image')) {
        let formData = new FormData
        formData.append("file",this.selectedFile)
        const url = 'http://127.0.0.1:5000/';
        this.http.post(url,formData).subscribe(response => {
          if(response['dangerous'] === '') {
            this.messages = [
              { severity: 'success', summary: 'SAFETY', detail: 'Everything good' },
            ];
            console.log(response['id'])

          }
          else {
            this.messages = [
              { severity: 'error', summary: 'DANGEROUS', detail: response['dangerous'] },
          ];
          }
          let filename = response['filename']
          this.imageURL = `../../assets/${filename}`
          this.title = response['dangerous']
          this.getResultByUserID()
          console.log(this.resultsByID)
        });
        
      } else if (this.selectedFile.type.includes('video')) {
        let formData = new FormData
        formData.append("file",this.selectedFile)
        const url = 'http://127.0.0.1:5000/upload_video';
        this.http.post(url,formData).subscribe(response => {
          this.link = `http://127.0.0.1:5000/video_feed_video/${response['filename']}`
          this.intervalId = setInterval(() => this.updateResult(), 2000);
          this.videoUrl =''
          this.imageURL = ''
          this.intervalId2 = setInterval(() => this.getResultByUserID(), 2000);

        });
      } else {
        console.log('Selected file is neither an image nor a video.');
      }
    }

  }
  
}
