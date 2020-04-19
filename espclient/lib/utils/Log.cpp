#include "Log.h"

 QLogger* QLogger::instance = NULL;

 QLogger*  QLogger :: getInstance() {
  if (!instance)
    instance = new QLogger();
  return instance ;
 }

 void QLogger :: beginSerial() {
   #ifndef __SERIALHASBEGUN__
   #define __SERIALHASBEGUN__
     Serial.begin(9600);
   #endif
 }

 const byte QLogger :: fromString(String lstring) {
  byte rLogger ; 
   if (lstring.equalsIgnoreCase("info"))
   {
      rLogger = QLogger :: LEVEL_INFO; 
   } else if (lstring.equalsIgnoreCase("debug"))
   {
      rLogger = QLogger :: LEVEL_DEBUG; 
   } else if (lstring.equalsIgnoreCase("error"))
   {
      rLogger = QLogger :: LEVEL_ERROR; 
   } else {
     rLogger = QLogger :: LEVEL_NONE ; 
   }
   return (const byte)rLogger; 
 }

 void QLogger::setLevel(byte loglevel) {
  this -> setLevel(loglevel, false) ;
 }

  void QLogger::setLevel(byte loglevel, bool forceLower)
  {
    QLogger :: beginSerial();
    Serial.println("Curl level = " + String(this -> log_level) + "; inlevel = " +
        String(loglevel) );
    if (forceLower) {
      this->log_level = loglevel ;
    }
    else if (loglevel > this->log_level) {
      this->log_level = loglevel ;
    }
    Serial.println("Set level to" + String(this -> log_level)); 
    if (loglevel > QLogger::LEVEL_NONE) {
      QLogger :: beginSerial();
      log(F("Set log level to "), String(log_level), log_level);
    }
  }

  byte QLogger::getLevel(){
    return this->log_level ;
  }

  void QLogger::log(String msg, byte level)  {
    if (level <= this->log_level) {
      Serial.println(msg) ;
    }
  }

  void QLogger::log(String msg, String m1, byte level) {
    if (level <= this->log_level) {
      Serial.println(msg+m1) ;
    }
  }
  void QLogger::log(String msg, String m1, String m2, byte level) {
    if (level <= this->log_level) {
      Serial.println(msg + m1 + m2) ;
    }
  }
  void QLogger::log(String msg, String m1, String m2, String m3, byte level) {
    if (level <= this->log_level) {
      Serial.println(msg + m1 + m2 + m3) ;
    }
  }

  void QLogger::log(String msg, String m1, String m2, String m3, String m4, byte level) {
    if (level <= this->log_level) {
      String mfull = msg ; 
      mfull.concat(m1); 
      mfull.concat(m2); 
      mfull.concat(m3); 
      mfull.concat(m4);
      Serial.println(mfull) ;
    }
  }

  void QLogger::log(String msg, int m1, byte level) {
    if (level <= this->log_level) {
      Serial.println(msg + String(m1)) ;
    }
  }

  void QLogger::info(String msg) {
    log(msg, QLogger::LEVEL_INFO);
  }
  void QLogger::info(String msg, String m1) {
    this -> log(msg, m1, QLogger::LEVEL_INFO);
  }

 void QLogger::info(String msg, String m1, String m2) {
    this -> log(msg, m1, m2, QLogger::LEVEL_INFO);
  }


  void QLogger::info(String msg, String m1, String m2, String m3) {
    this -> log(msg, m1, m2, m3, QLogger::LEVEL_INFO);
  }

  void QLogger::info(String msg, int m1) {
    this -> log(msg, m1, QLogger::LEVEL_INFO);
  }


  void QLogger::debug(String msg) {
    log(msg, QLogger::LEVEL_DEBUG);
  }

  void QLogger::debug(String msg, String m1) {
    this -> log(msg, m1, QLogger::LEVEL_DEBUG) ;
  }

  void QLogger::debug(String msg, String m1, String m2) {
    this -> log(msg, m1, m2, QLogger::LEVEL_DEBUG) ;
  }

  void QLogger::debug(String msg, String m1, String m2, String m3) {
    this -> log(msg, m1, m2, m3, QLogger::LEVEL_DEBUG) ;
  }
  void QLogger::debug(String msg, String m1, String m2, String m3, String m4) {
    this -> log(msg, m1, m2, m3, m4, QLogger::LEVEL_DEBUG) ;
  }

  void QLogger::debug(String msg, int m1) {
    this -> log(msg, m1, QLogger::LEVEL_DEBUG) ;
  }

   void QLogger::error(String msg) {
    log(msg, QLogger::LEVEL_ERROR);
  }

  void QLogger::error(String msg, String m1) {
    this -> log(msg, m1, QLogger::LEVEL_ERROR) ;
  }

  void QLogger::error(String msg, String m1, String m2) {
    this -> log(msg, m1, m2, QLogger::LEVEL_ERROR) ;
  }

  void QLogger::error(String msg, String m1, String m2, String m3) {
    this -> log(msg, m1, m2, m3, QLogger::LEVEL_ERROR) ;
  }

  void QLogger::error(String msg, String m1, String m2, String m3, String m4) {
    this -> log(msg, m1, m2, m3, m4, QLogger::LEVEL_ERROR) ;
  }

  void QLogger::error(String msg, int m1) {
    this -> log(msg, m1, QLogger::LEVEL_ERROR) ;
  }

  // private log function 
/* 
  void QLogger:: logvariadic(const char* msg, const byte level ...)  {
    if (level <= this->log_level) {

      // not yet implemented. Will do later on 
      Serial.println(msg); 
    }

  }
  */
  

