import { Injectable } from "@angular/core";


import { MessageService } from "primeng/api";
import Swal, { SweetAlertResult } from "sweetalert2";
import { SeverityEnum, SummaryEnum } from "./toast.enum";

@Injectable({
  providedIn: "root"
})
export class ToastMessageService {
  constructor(private messageService: MessageService) {}

  showSuccessMessage(prefix: string, contentType: string, custom?: string) {
    this.messageService.add({
      severity: SeverityEnum.Success,
      summary: SummaryEnum.Success,
      detail: !custom ? `${prefix} ${contentType} thành công!` : custom
    });
  }

  showErrorMessage(prefix: string, contentType: string, custom?: string) {
    this.messageService.add({
      severity: SeverityEnum.Error,
      summary: SummaryEnum.Error,
      detail: !custom ? `${prefix} ${contentType} thất bại!` : custom
    });
  }

  showNotificationSwal(text: string) {
    Swal.fire({
      icon: "warning",
      title: "Thông báo",
      text: text
    }).then();
  }

  showSuccessSwal(text: string) {
    Swal.fire({
      icon: "success",
      title: "Thành công",
      text: text
    }).then();
  }

  showErrorSwal(text: string) {
    Swal.fire({
      icon: "error",
      title: "Lỗi...",
      text: text
    }).then();
  }

  showConfirmDeleteSwal(object: string, name: string): Promise<SweetAlertResult<any>> {
    return Swal.fire({
      title: "Bạn có chắc chắn ?",
      text: `${object} ${name} sẽ được xoá!`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3b82f6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Xoá",
      cancelButtonText: "Huỷ"
    });
  }
}
