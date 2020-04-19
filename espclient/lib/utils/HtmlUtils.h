#ifndef __HTMLUTIlS_H__
#define __HTMLUTIlS_H__
#include <Arduino.h>

#define ENC20 "%20"
#define ENC20_2 "+"
#define DEC20 " "
#define ENC21 "%21"
#define DEC21 "!"
#define ENC23 "%23"
#define DEC23 "#"
#define ENC24 "%24"
#define DEC24 "$"
#define ENC26 "%26"
#define DEC26 "&"
#define DEC27 "'"
#define ENC27 "%27"
#define DEC28  "("
#define ENC28 "%28"
#define DEC29 ")"
#define ENC29 "%29"
#define DEC2A "*"
#define ENC2A "%2A"
#define DEC2B "+"
#define ENC2B "%2B"
#define DEC2C ","
#define ENC2C "%2C"
#define DEC2F "/"
#define ENC2F "%2F"
#define DEC3A ":"
#define ENC3A "%3A"
#define DEC3B ";"
#define ENC3B "%3B"
#define DEC3D "="
#define ENC3D "%3D"
#define DEC3F "?"
#define ENC3F "%3F"
#define DEC40  "@"
#define ENC40 "%40"
#define DEC5B "["
#define ENC5B "%5B"
#define DEC5D "]"
#define ENC5D "%5D"

class HtmlUtils {
public:
  static String UrlDecode(String encoded);
  static String UrlEncode(String );

};

#endif
