export class Result{
    public ResultID?: number;
    public UserID: string = "";
    public NgayTest: Date;
    public LinkImg: string="";
    public TenBenh: string=""
    public DoChinhXac: number;
    constructor(ResultID: number, UserID: string, NgayTest: Date, LinkImg: string, DoChinhXac: number, TenBenh: string){
        this.ResultID = ResultID
        this.UserID = UserID
        this.NgayTest = NgayTest
        this.LinkImg = LinkImg
        this.DoChinhXac = DoChinhXac
        this.TenBenh = TenBenh
      }
}