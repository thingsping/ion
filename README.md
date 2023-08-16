# ion
Repository for all ION compliant implementations. The ION Specification itself is a separate repository. 
    https://github.com/thingsping/IONMP

A few students from BITS Pilani's special track post graduation program on IOT, as part of our capstone project, wanted to work on an IOT platform that was protocol, vendor and hardware agnostic. Thus the IONMP Framework and the related products were born!. After some deliberation, we decided to make this into an opensource project. We started the code commit process into this opensource repository in March 2020. 

Things started moving a bit slow, mainly due to the global effect of the lockdown caused by the COVID-19 pandemic. All of us are working on our free time on the ion project and our main work schedule during these challenging times have been a bit more hectic than normal. However we still try to squeeze in some time and have been making small progress. 

Folders in this repository:
## pythonsrv ##
Python implementation of an IONMP compliant server. This server implements most of the important aspects of the IONMP protocol. The following parts have still not been implemented:
- Two step authentication using MD5 Hash
- SUBSCRIBE and NOTIFY messages
  - Instead of the standard SUBSCRIBE, NOTIFY, in this server we use a technique where event-action relationships (which achieves the core functionality of SUBSCRIBE / NOTIFY) is embedded into the server code itself. 
- BLOCKLY based event-action configuration
  - We intend to push this into the repository as soon as we have the first set of client implementations / examples ready. 
