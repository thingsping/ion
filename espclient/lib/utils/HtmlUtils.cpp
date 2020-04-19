#include "HtmlUtils.h"

String HtmlUtils :: UrlDecode(String param){
    param.replace(ENC20,DEC20);
    param.replace(ENC20_2, DEC20); 
    param.replace(ENC21,DEC21);
    param.replace(ENC23,DEC23);
    param.replace(ENC24,DEC24);
    param.replace(ENC26,DEC26);
    param.replace(ENC27,DEC27);
    param.replace(ENC28,DEC28);
    param.replace(ENC29,DEC29);
    param.replace(ENC2A,DEC2A);
    param.replace(ENC2B,DEC2B);
    param.replace(ENC2C,DEC2C);
    param.replace(ENC2F,DEC2F);
    param.replace(ENC3A,DEC3A);
    param.replace(ENC3B,DEC3B);
    param.replace(ENC3D,DEC3D);
    param.replace(ENC3F,DEC3D);
    param.replace(ENC40,DEC40);
    param.replace(ENC5B,DEC5B);
    param.replace(ENC5D,DEC5D);
    return param ;
}

String HtmlUtils :: UrlEncode(String param){
    param.replace(DEC20, ENC20);
    param.replace(DEC21, ENC21);
    param.replace(DEC23, ENC23);
    param.replace(DEC24, ENC24);
    param.replace(DEC26, ENC26);
    param.replace(DEC27, ENC27);
    param.replace(DEC28, ENC28);
    param.replace(DEC29, ENC29);
    param.replace(DEC2A, ENC2A);
    param.replace(DEC2B, ENC2B);
    param.replace(DEC2C, ENC2C);
    param.replace(DEC2F, ENC2F);
    param.replace(DEC3A, ENC3A);
    param.replace(DEC3B, ENC3B);
    param.replace(DEC3D, ENC3D);
    param.replace(DEC3D, ENC3F);
    param.replace(DEC40, ENC40);
    param.replace(DEC5B, ENC5B);
    param.replace(DEC5D, ENC5D);
    return param ;
}