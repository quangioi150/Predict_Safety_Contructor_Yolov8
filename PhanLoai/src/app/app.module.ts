import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {TabViewModule} from 'primeng/tabview';
import {ButtonModule} from 'primeng/button';
import { LoginComponent } from './login/login.component';
import {CheckboxModule} from 'primeng/checkbox';
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import {DividerModule} from 'primeng/divider';
import {CalendarModule} from 'primeng/calendar';
import { CardModule } from 'primeng/card';
import { MessageService } from 'primeng/api';
import {InputTextModule} from 'primeng/inputtext';
import { ClassifyComponent } from './classify/classify.component';
import {FileUploadModule} from 'primeng/fileupload';
import {HttpClientModule} from '@angular/common/http';
import {TableModule} from 'primeng/table';
import {ToastModule} from 'primeng/toast';
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import {InplaceModule} from 'primeng/inplace';
import { UserUpdateComponent } from './user-update/user-update.component';
import {DynamicDialogModule} from 'primeng/dynamicdialog';
@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    ClassifyComponent,
    UserUpdateComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    InputTextModule,
    TabViewModule,
    ButtonModule,
    FormsModule,
    ReactiveFormsModule,
    CheckboxModule,
    DividerModule,
    CalendarModule,
    FileUploadModule,
    HttpClientModule,
    TableModule,
    ToastModule,
    BrowserAnimationsModule,
    InplaceModule,
    DynamicDialogModule,
    CardModule
  ],
  providers: [MessageService],
  bootstrap: [AppComponent]
})
export class AppModule { }
