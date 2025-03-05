一、传输起始标志
    长度：4字节
    内容：0XAE  0XAE  0XAE  0XAE  
二、消息长度
    长度：2字节（16进制表示）
    计算方法：模式标志+纸币信息+传输结束标志
        2+1644+4=1650
三、模式标志
    长度：2字节
    内容：0X0001 
四：纸币信息
    长度：1644字节
    内容：请查看附件2（不包括文件头）
	typedef struct {
        Uint16 Date;		  	//验钞启动日期
        Uint16 Time;		  	//验钞启动时间
        Uint16 tfFlag;		//真、假、残和旧币标志
        Uint32 Valuta32;  //币值
        Uint16 FSN_COUNT;  //纸币计数 
        Uint16 MoneyFlag[4]; 	//货币标志
        Uint16 Ver;           //版本号
        Uint16 undefine;		//币值
        Uint16 CharNUM;	  	//冠字号码字符数
        Uint16 SNo[12];		//冠字号码
        Uint16 MachineSNo[24];//机具编号
        Uint16 Reserve1       //保留字1
        TImageSNo ImageSNo;//图像冠字号码
    } 

typedef struct {
    Int16 undefine[4];  //  
    UInt8  SNo[1536];  //96*16的BMP图像

} TImageSNo;//图像冠字号码结构

五：传输结束标志
    长度：4字节
    内容：0XBE  0XBE  0XBE  0XBE  