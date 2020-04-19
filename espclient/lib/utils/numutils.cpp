#include "numutils.h"

bool NumUtils :: isNumeric(String sNum)
{
  bool isNumeric = false ;
  for (unsigned int i = 0 ; i < sNum.length(); i++)
  {
    char c = sNum.charAt(i);
    int tempNum = c - '0';
    if (tempNum == -2 || ( tempNum >=0 && tempNum <= 9 ))
    {
      isNumeric = true ;
    }
    else {
      isNumeric = false ;
      break ;
    }
  }

  return isNumeric ;
}

bool NumUtils :: isNumeric(char* sNum){
  bool isNumeric = false ;
  for (unsigned int i = 0 ; i < strlen(sNum); i++)
  {
    char c = sNum[i];
    int tempNum = c - '0';
    // Check not for just numbers but also for the characters - 
    // '.', '-' or '+'
    if (tempNum == -2 || tempNum == -3 || tempNum == -5 ||
         ( tempNum >=0 && tempNum <= 9 ))
    {
      isNumeric = true ;
    }
    else {
      isNumeric = false ;
      break ;
    }
  }
  return isNumeric ; 
}
