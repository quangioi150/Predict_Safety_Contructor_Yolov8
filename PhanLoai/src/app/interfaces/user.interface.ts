export class User{
    public UserID?: number;
    public HoTen: string="";
    public TenDN: string="";
    public NgaySinh: string="";
    public DiaChi: string="";
    public MatKhau: string
    constructor(UserID: number, HoTen: string, TenDN: string, NgaySinh: string, DiaChi: string, MatKhau: string){
        this.UserID = UserID
        this.HoTen = HoTen
        this.TenDN = TenDN
        this.NgaySinh = NgaySinh
        this.DiaChi = DiaChi
        this.MatKhau =MatKhau
      }
}

