#ifndef __IONCONSTANTS_H__
#define __IONCONSTANTS_H__

#define CONFIGPIN 3
#define ONBOARDLED 2 
#define HDRTYPE "Type"
#define HDRVER "Ver"
#define HDRFROM "From"
#define HDRDEVID "Nid"
#define HDRMID "Mid"
#define HDRTIME "Time "
#define HDRDATA "Data"
#define HDRNAME "Name"
#define HDRNODETYPE "NodeType"
#define HDRLOCATION "Location"
#define HDRACTION "Action"
#define HDRCAPABILITIES "Capabilities"
#define HDRPARAMS "Parameters"
#define HDRRETURN "Return"
#define HDRCONTROLMETHOD "ControlMethod"
#define CONTROLMETHODPOLL "Poll"
#define CONTROLMETHODDEAMON "Deamon"
#define HDREXPIRES "Expires"
#define HDRKEY "Key"
#define HDRNONCE "Nonce"
#define HDRCFGHASH "Chash"
#define HDRCONFIG "Config"

#define VERVAL "0.5"
#define TYPEADV "Advertise"
#define TYPEREG "Register"
#define TYPEPUB "Publish"
#define TYPECTL "Control"
#define TYPECFG "GETCONFIG"
#define TYPECTLPOLL "POLLCONTROL"

#define RESPONSEINVALID 0
#define RESPONSEOK 200
#define RESPONSEACCEPTED 202
#define RESPONSEUNAUTH 401
#define RESPONSEFORBIDDEN 403
#define RESPONSENOTFOUND 404

#define MAXRETRIES 3
#define DEFAULTTIMEOUT 30000
#define ADSIZE 2048
#define CTLSIZE 512
#define CFGSIZE 512
#define DEFAULTSERVER "ion.thingsping.in"
#define DEFAULTCONFIGSERVER "config.thingsping.in"
#define NOCONFIGSERVER "NONE"
#define DEFAULTPORT 80
#define UDPPOLLPORT 52000
#define DEFAULTPOLLINGPORT 10560
#define DEFEXPIRESTIME 3600
#define DEFAULTLOCATION "Unallocated"

#define JSON200  "{\"Type\":200}"
#define JSON202  "{\"Type\":202}"
#define JSON400  "{\"Type\":400}"
#define JSON404  "{\"Type\":404}"
#define JSON403  "{\"Type\":403}"
#define JSON500  "{\"Type\":500}"

#define RESPONSETEMPLATE "HTTP/1.1 200 OK\n" \
            "Content-Type: text/html; charset=UTF-8\n" \
            "Server: ION-Node\n" \
            "X-freemem: %FREEMEM%\n" \
            "X-processingtime: %TOTALTIME%\n" \
            "X-uptime: %UPTIME%\n" \
            "Content-Length: %CONTENTLEN%\n\n"

#define WINOTSTR "WiNoT"

enum CcshError {ERR_SUCCESS, ERR_NULLPOINTER, ERR_PAIR_LENGTH_MISMATCH, 
    ERR_INVALID_ARGUMENT, ERR_KEY_NOTDEFINED, ERR_PARAMS_ARE_STRINGS, 
    ERR_EMPTY_ARRAY };

enum NodeType {UndefinedNode, SensorDevice, OutputDevice};
enum ValueType {UnknownType, Str, Int, Float, Boolean};

enum HttpMethod {UnknownMethod, Get, Post, Put, Delete, Response}; 
enum BlinkType {NoBlink, FastBlink, SlowBlink, AirplaneBlink};
enum LogLevel {LevelNoLogging, LevelInfolog, LevelErrlog, LevelDebuglog}; 

#endif 