#ifndef __QLOGGER_H__
#define __QLOGGER_H__
#include "Arduino.h"


class QLogger
{
 public:
  static const byte LEVEL_NONE = 0 ;
  static const byte LEVEL_ERROR = 3;
  static const byte LEVEL_INFO = 6;
  static const byte LEVEL_DEBUG = 10;

  static const byte fromString(String lstring);

  static QLogger* getInstance();
  static void beginSerial() ;

  void setLevel(byte level) ;
  void setLevel(byte level, bool force) ;
  byte getLevel() ;
	void info(String msg) ;
  void info(String msg, String m1) ;
  void info(String msg, String m1, String m2);
  void info(String msg, String m1, String m2, String m3);
  void info(String msg, int m1) ;
  
  void debug(String msg) ;
  void debug(String msg, String m1);
  void debug(String msg, String m1, String m2);
  void debug(String msg, String m1, String m2, String m3);
  void debug(String msg, String m1, String m2, String m3, String m4);
  void debug(String msg, int m1) ;

  //void debug(char* tpl ...); 
  //void info(char* tpl ...); 
  //void error(char* tpl ...); 


  void error(String msg) ;
  void error(String msg, String m1);
  void error(String msg, String m1, String m2);
  void error(String msg, String m1, String m2, String m3);
  void error(String msg, String m1, String m2, String m3, String m4);
  void error(String msg, int m1) ;

 private:
  static bool hasBegun ;
  QLogger(){};
  QLogger(QLogger const&){};             // copy constructor is private
  QLogger& operator=(QLogger const&){return *instance;};  // assignment operator is private
  static QLogger* instance ;
	byte log_level ;


  void log(String msg, byte level) ;
  void log(String msg, String m1, byte level) ;
  void log(String msg, String m1, String m2, byte level) ;
  void log(String msg, String m1, String m2, String m3, byte level) ;
  void log(String msg, String m1, String m2, String m3, String m4, byte level) ;
  void log(String msg, int m1, byte level) ;

  void logvariadic(const char* tpl, const byte level ...); 
} ;


#endif
